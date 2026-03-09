from __future__ import annotations

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


class ParkingRecordCommandService:
    def __init__(
        self,
        *,
        parking_record_repository: ParkingRecordRepository | None = None,
        vehicle_repository: VehicleRepository | None = None,
    ) -> None:
        self.parking_record_repository = parking_record_repository or DjangoParkingRecordRepository()
        self.vehicle_repository = vehicle_repository or DjangoVehicleRepository()

    @transaction.atomic
    def create_entry(self, *, command: EntryCommand) -> ParkingRecordSnapshot:
        if not self.vehicle_repository.exists(vehicle_num=command.vehicle_num):
            raise ParkingRecordNotFoundError("존재하지 않는 차량입니다.")

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
            self.parking_record_repository.save_history(history=history)
            occupancy.occupy(
                vehicle_num=command.vehicle_num,
                history=history,
                occupied_at=command.entry_at or history.entry_at,
            )
            self.parking_record_repository.save_occupancy(occupancy=occupancy)
        except (IntegrityError, DatabaseError) as exc:
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

        occupancy.release()
        self.parking_record_repository.save_occupancy(occupancy=occupancy)

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
