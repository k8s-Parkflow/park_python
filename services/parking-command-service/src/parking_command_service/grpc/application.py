from __future__ import annotations

from datetime import datetime

from django.db import transaction
from django.utils import timezone

from parking_command_service.domains.parking_record.application.dtos import EntryCommand
from parking_command_service.domains.parking_record.application.exceptions import (
    ParkingRecordNotFoundError,
)
from parking_command_service.domains.parking_record.application.services import (
    ParkingRecordCommandService,
)
from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingRecordRepository,
    DjangoVehicleRepository,
)


class ParkingCommandGrpcApplicationService:
    def __init__(
        self,
        *,
        parking_record_repository: DjangoParkingRecordRepository | None = None,
        command_service: ParkingRecordCommandService | None = None,
    ) -> None:
        repository = parking_record_repository or DjangoParkingRecordRepository()
        self.parking_record_repository = repository
        self.command_service = command_service or ParkingRecordCommandService(
            parking_record_repository=repository,
            vehicle_repository=DjangoVehicleRepository(),
            projection_writer=None,
        )

    def create_entry(
        self,
        *,
        vehicle_num: str,
        slot_id: int,
        requested_at: datetime | None,
    ):
        slot = self._get_slot_or_raise(slot_id=slot_id)
        return self.command_service.create_entry(
            command=EntryCommand(
                vehicle_num=vehicle_num,
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                entry_at=requested_at,
            )
        )

    @transaction.atomic
    def compensate_entry(self, *, history_id: int) -> dict:
        history = self.parking_record_repository.get_history_for_update(history_id=history_id)
        if history is None:
            raise ParkingRecordNotFoundError("존재하지 않는 주차 이력입니다.")

        occupancy = self.parking_record_repository.get_or_create_occupancy_for_update(slot=history.slot)
        compensated_at = history.exit_at or timezone.now()

        if history.exit_at is None:
            history.exit(exited_at=compensated_at)
            self.parking_record_repository.save_history(history=history)
        if occupancy.occupied:
            occupancy.release()
            self.parking_record_repository.save_occupancy(occupancy=occupancy)

        return {
            "history_id": history.history_id,
            "slot_released": not occupancy.occupied,
            "compensated_at": history.exit_at or compensated_at,
        }

    def _get_slot_or_raise(self, *, slot_id: int):
        slot = self.parking_record_repository.get_slot(slot_id=slot_id)
        if slot is None:
            raise ParkingRecordNotFoundError("존재하지 않는 슬롯입니다.")
        return slot
