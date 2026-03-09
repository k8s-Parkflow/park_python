from __future__ import annotations

import time
from typing import Protocol

from django.db import DatabaseError, IntegrityError, transaction
from django.utils import timezone

from parking_command_service.dtos import EntryCommand, ExitCommand, ParkingRecordSnapshot
from parking_command_service.exceptions import (
    ParkingRecordConflictError,
    ParkingRecordNotFoundError,
)
from parking_command_service.models import ParkingHistory, SlotOccupancy
from parking_command_service.repositories import (
    DjangoParkingRecordRepository,
    DjangoVehicleRepository,
)


class ParkingRecordRepository(Protocol):
    def get_slot_for_update(self, *, slot_id: int): ...
    def get_or_create_occupancy_for_update(self, *, slot): ...
    def has_active_history_for_vehicle(self, *, vehicle_num: str) -> bool: ...
    def get_active_history_for_vehicle_for_update(self, *, vehicle_num: str): ...
    def save_history(self, *, history: ParkingHistory) -> ParkingHistory: ...
    def save_occupancy(self, *, occupancy: SlotOccupancy) -> SlotOccupancy: ...


class VehicleRepository(Protocol):
    def exists(self, *, vehicle_num: str) -> bool: ...


class ParkingProjectionWriter(Protocol):
    def record_entry(self, *, history: ParkingHistory) -> None: ...
    def record_exit(self, *, history: ParkingHistory) -> None: ...


class ParkingRecordCommandService:
    def __init__(
        self,
        *,
        parking_record_repository: ParkingRecordRepository | None = None,
        vehicle_repository: VehicleRepository | None = None,
        projection_writer: ParkingProjectionWriter | None = None,
    ) -> None:
        self.parking_record_repository = parking_record_repository or DjangoParkingRecordRepository()
        self.vehicle_repository = vehicle_repository or DjangoVehicleRepository()
        self.projection_writer = projection_writer

    def create_entry(self, *, command: EntryCommand) -> ParkingRecordSnapshot:
        for attempt in range(3):
            try:
                return self._create_entry_once(command=command)
            except DatabaseError as exc:
                if not _is_locked_error(exc) or attempt == 2:
                    raise ParkingRecordConflictError("입차 처리 중 충돌이 발생했습니다.") from exc
                time.sleep(0.01)

        raise ParkingRecordConflictError("입차 처리 중 충돌이 발생했습니다.")

    @transaction.atomic
    def _create_entry_once(self, *, command: EntryCommand) -> ParkingRecordSnapshot:
        if not self.vehicle_repository.exists(vehicle_num=command.vehicle_num):
            raise ParkingRecordNotFoundError("존재하지 않는 차량입니다.")

        # 슬롯과 점유 행을 같은 트랜잭션 안에서 잠가 이중 입차를 줄이는 흐름
        slot = self.parking_record_repository.get_slot_for_update(slot_id=command.slot_id)
        if slot is None:
            raise ParkingRecordNotFoundError("존재하지 않는 슬롯입니다.")

        occupancy = self.parking_record_repository.get_or_create_occupancy_for_update(slot=slot)
        if not slot.is_active:
            raise ParkingRecordConflictError("비활성화된 슬롯입니다.")
        if occupancy.occupied:
            raise ParkingRecordConflictError("이미 점유 중인 슬롯입니다.")
        if self.parking_record_repository.has_active_history_for_vehicle(vehicle_num=command.vehicle_num):
            raise ParkingRecordConflictError("이미 활성 주차 세션이 존재합니다.")

        history = ParkingHistory.start(
            slot=slot,
            vehicle_num=command.vehicle_num,
            entry_at=command.entry_at or timezone.now(),
        )

        try:
            # 이력 저장 후 점유를 연결해야 현재 활성 세션 참조가 일관된다.
            self.parking_record_repository.save_history(history=history)
            occupancy.occupy(
                vehicle_num=command.vehicle_num,
                history=history,
                occupied_at=command.entry_at or history.entry_at,
            )
            self.parking_record_repository.save_occupancy(occupancy=occupancy)
            if self.projection_writer is not None:
                # command 완료 시점의 write 결과만 query projection에 반영한다.
                self.projection_writer.record_entry(history=history)
        except IntegrityError as exc:
            raise ParkingRecordConflictError("입차 처리 중 충돌이 발생했습니다.") from exc

        return _build_snapshot(history=history)

    @transaction.atomic
    def create_exit(self, *, command: ExitCommand) -> ParkingRecordSnapshot:
        history = self.parking_record_repository.get_active_history_for_vehicle_for_update(
            vehicle_num=command.vehicle_num
        )
        if history is None:
            raise ParkingRecordNotFoundError("활성 주차 이력이 없습니다.")

        occupancy = self.parking_record_repository.get_or_create_occupancy_for_update(slot=history.slot)
        exit_at = command.exit_at or timezone.now()
        history.exit(exited_at=exit_at)
        self.parking_record_repository.save_history(history=history)

        # 출차 이력 종료와 점유 해제는 같은 트랜잭션에서 함께 끝나야 한다.
        occupancy.release()
        self.parking_record_repository.save_occupancy(occupancy=occupancy)
        if self.projection_writer is not None:
            self.projection_writer.record_exit(history=history)

        return _build_snapshot(history=history)


def _build_snapshot(*, history: ParkingHistory) -> ParkingRecordSnapshot:
    return ParkingRecordSnapshot(
        history_id=history.history_id,
        vehicle_num=history.vehicle_num,
        slot_id=history.slot_id,
        status=history.status,
        entry_at=history.entry_at,
        exit_at=history.exit_at,
    )


def _is_locked_error(exc: DatabaseError) -> bool:
    return "locked" in str(exc).lower()
