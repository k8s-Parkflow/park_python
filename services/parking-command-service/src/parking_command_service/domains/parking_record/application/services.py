from __future__ import annotations

import time
from typing import Protocol

from django.db import DatabaseError, IntegrityError, transaction
from django.utils import timezone

from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient
from parking_command_service.domains.parking_record.application.dtos import (
    EntryCommand,
    ExitCommand,
    ParkingRecordSnapshot,
    SlotCommand,
)
from parking_command_service.domains.parking_record.application.exceptions import (
    ParkingRecordBadRequestError,
    ParkingRecordConflictError,
    ParkingRecordNotFoundError,
)
from parking_command_service.domains.parking_record.domain import ParkingHistory, SlotOccupancy
from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingRecordRepository,
)
from parking_command_service.global_shared.utils.vehicle_nums import normalize_vehicle_num


class ParkingRecordRepository(Protocol):
    def get_lock_anchor_for_update(self, *, slot_id: int): ...
    def get_lock_anchor_by_identity_for_update(self, *, zone_id: int, slot_code: str): ...
    def get_or_create_occupancy_for_update(self, *, lock_anchor): ...
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
        self.vehicle_repository = vehicle_repository or VehicleGrpcClient()
        self.projection_writer = projection_writer

    def create_entry(self, *, command: EntryCommand) -> ParkingRecordSnapshot:
        return self._run_entry(command=command, trust_zone_metadata=False)

    def create_trusted_entry(self, *, command: EntryCommand) -> ParkingRecordSnapshot:
        return self._run_entry(command=command, trust_zone_metadata=True)

    def _run_entry(
        self,
        *,
        command: EntryCommand,
        trust_zone_metadata: bool,
    ) -> ParkingRecordSnapshot:
        for attempt in range(3):
            try:
                return self._create_entry_once(
                    command=command,
                    trust_zone_metadata=trust_zone_metadata,
                )
            except DatabaseError as exc:
                if not _is_locked_error(exc) or attempt == 2:
                    raise ParkingRecordConflictError("입차 처리 중 충돌이 발생했습니다.") from exc
                time.sleep(0.01)

        raise ParkingRecordConflictError("입차 처리 중 충돌이 발생했습니다.")

    @transaction.atomic
    def _create_entry_once(
        self,
        *,
        command: EntryCommand,
        trust_zone_metadata: bool,
    ) -> ParkingRecordSnapshot:
        if trust_zone_metadata:
            _validate_trusted_slot_snapshot(command=command)
        vehicle_num = _normalize_lookup_vehicle_num(command.vehicle_num)
        if not self.vehicle_repository.exists(vehicle_num=vehicle_num):
            raise ParkingRecordNotFoundError("존재하지 않는 차량입니다.")

        # lock anchor와 점유 행을 같은 트랜잭션 안에서 잠가 이중 입차를 줄인다.
        lock_anchor = self._resolve_lock_anchor(
            command=command,
            trust_zone_metadata=trust_zone_metadata,
        )

        occupancy = self.parking_record_repository.get_or_create_occupancy_for_update(
            lock_anchor=lock_anchor
        )
        if not trust_zone_metadata and not lock_anchor.is_active:
            raise ParkingRecordConflictError("비활성화된 슬롯입니다.")
        if occupancy.occupied:
            raise ParkingRecordConflictError("이미 점유 중인 슬롯입니다.")
        if self.parking_record_repository.has_active_history_for_vehicle(vehicle_num=vehicle_num):
            raise ParkingRecordConflictError("이미 활성 주차 세션이 존재합니다.")

        history = ParkingHistory.start(
            slot=lock_anchor,
            vehicle_num=vehicle_num,
            entry_at=command.entry_at or timezone.now(),
            zone_id=command.zone_id,
            slot_type_id=_resolve_slot_type_id(command=command, lock_anchor=lock_anchor),
            slot_code=command.slot_code,
        )

        try:
            # 이력 저장 후 점유를 연결해야 현재 활성 세션 참조가 일관된다.
            self.parking_record_repository.save_history(history=history)
            occupancy.occupy(
                vehicle_num=vehicle_num,
                history=history,
                occupied_at=command.entry_at or history.entry_at,
                enforce_slot_active=not trust_zone_metadata,
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
        vehicle_num = _normalize_lookup_vehicle_num(command.vehicle_num)
        history = self.parking_record_repository.get_active_history_for_vehicle_for_update(
            vehicle_num=vehicle_num
        )
        if history is None:
            raise ParkingRecordNotFoundError("활성 주차 이력이 없습니다.")

        self._validate_exit_request(history=history, command=command)

        occupancy = self.parking_record_repository.get_or_create_occupancy_for_update(
            lock_anchor=history.slot
        )
        exit_at = command.exit_at or timezone.now()
        history.exit(exited_at=exit_at)
        self.parking_record_repository.save_history(history=history)

        # 출차 이력 종료와 점유 해제는 같은 트랜잭션에서 함께 끝나야 한다.
        occupancy.release()
        self.parking_record_repository.save_occupancy(occupancy=occupancy)
        if self.projection_writer is not None:
            self.projection_writer.record_exit(history=history)

        return _build_snapshot(history=history)

    def _resolve_lock_anchor(
        self,
        *,
        command: SlotCommand,
        trust_zone_metadata: bool,
    ):
        anchor_by_id = self.parking_record_repository.get_lock_anchor_for_update(slot_id=command.slot_id)
        if anchor_by_id is None:
            raise ParkingRecordNotFoundError("존재하지 않는 슬롯입니다.")
        if trust_zone_metadata:
            return anchor_by_id
        anchor_by_identity = self.parking_record_repository.get_lock_anchor_by_identity_for_update(
            zone_id=command.zone_id,
            slot_code=command.slot_code,
        )
        if anchor_by_identity is None:
            raise ParkingRecordBadRequestError("슬롯 식별자가 서로 일치하지 않습니다.")
        if anchor_by_id.slot_id != anchor_by_identity.slot_id:
            raise ParkingRecordBadRequestError("슬롯 식별자가 서로 일치하지 않습니다.")
        return anchor_by_id

    def _validate_exit_request(self, *, history: ParkingHistory, command: ExitCommand) -> None:
        if command.slot_id != history.slot_id:
            raise ParkingRecordConflictError("출차 요청 위치가 현재 점유 위치와 일치하지 않습니다.")
        if command.zone_id != _history_zone_id(history):
            raise ParkingRecordConflictError("출차 요청 위치가 현재 점유 위치와 일치하지 않습니다.")
        if command.slot_code != _history_slot_code(history):
            raise ParkingRecordConflictError("출차 요청 위치가 현재 점유 위치와 일치하지 않습니다.")


def _build_snapshot(*, history: ParkingHistory) -> ParkingRecordSnapshot:
    return ParkingRecordSnapshot(
        history_id=history.history_id,
        vehicle_num=history.vehicle_num,
        zone_id=_history_zone_id(history),
        slot_code=_history_slot_code(history),
        slot_id=history.slot_id,
        status=history.status,
        entry_at=history.entry_at,
        exit_at=history.exit_at,
    )


def _is_locked_error(exc: DatabaseError) -> bool:
    return "locked" in str(exc).lower()


def _normalize_lookup_vehicle_num(vehicle_num: str) -> str:
    return normalize_vehicle_num(vehicle_num)


def _validate_trusted_slot_snapshot(*, command: EntryCommand) -> None:
    if not command.slot_type:
        raise ParkingRecordBadRequestError("trusted 입차에는 slot_type이 필요합니다.")


def _history_zone_id(history) -> int:
    zone_id = getattr(history, "zone_id", 0) or 0
    if zone_id:
        return zone_id
    return history.slot.zone_id


def _history_slot_code(history) -> str:
    slot_code = getattr(history, "slot_code", "")
    if slot_code:
        return slot_code
    return history.slot.slot_code


def _resolve_slot_type_id(*, command: EntryCommand, lock_anchor) -> int:
    if command.slot_type is None:
        return lock_anchor.slot_type_id
    return {
        "GENERAL": 1,
        "EV": 2,
        "DISABLED": 3,
    }.get(command.slot_type, lock_anchor.slot_type_id)
