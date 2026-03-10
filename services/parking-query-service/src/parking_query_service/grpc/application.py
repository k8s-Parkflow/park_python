from __future__ import annotations

from datetime import datetime

from django.utils import timezone

from parking_query_service.repositories.current_location_repository import CurrentLocationRepository
from parking_query_service.repositories.zone_availability_repository import ZoneAvailabilityRepository
from parking_query_service.services.zone_availability_service import ZoneAvailabilityService


class ParkingQueryProjectionNotFoundError(Exception):
    pass


class ParkingQueryGrpcApplicationService:
    def __init__(
        self,
        *,
        current_location_repository: CurrentLocationRepository | None = None,
        zone_availability_service: ZoneAvailabilityService | None = None,
    ) -> None:
        self.current_location_repository = current_location_repository or CurrentLocationRepository()
        self.zone_availability_service = zone_availability_service or ZoneAvailabilityService(
            zone_availability_repository=ZoneAvailabilityRepository()
        )

    def apply_entry_projection(
        self,
        *,
        history_id: int,
        vehicle_num: str,
        slot_id: int,
        slot_code: str,
        zone_id: int,
        slot_type: str,
        entry_at: datetime | None,
    ) -> dict:
        projection = self._save_projection(
            history_id=history_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            slot_code=slot_code,
            zone_id=zone_id,
            slot_type=slot_type,
            entry_at=entry_at,
        )
        return {
            "projected": True,
            "updated_at": projection.updated_at,
        }

    def apply_exit_projection(self, *, history_id: int, vehicle_num: str) -> dict:
        projection = self.current_location_repository.get_by_vehicle_num(vehicle_num)
        if projection is not None and projection.history_id == history_id:
            self.current_location_repository.delete_projection(vehicle_num=vehicle_num)
        return {
            "projected": True,
            "updated_at": timezone.now(),
        }

    def compensate_entry_projection(self, *, vehicle_num: str) -> dict:
        self.current_location_repository.delete_projection(vehicle_num=vehicle_num)
        return {
            "compensated": True,
            "updated_at": timezone.now(),
        }

    def compensate_exit_projection(
        self,
        *,
        history_id: int,
        vehicle_num: str,
        slot_id: int,
        slot_code: str,
        zone_id: int,
        slot_type: str,
        entry_at: datetime | None,
    ) -> dict:
        projection = self._save_projection(
            history_id=history_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            slot_code=slot_code,
            zone_id=zone_id,
            slot_type=slot_type,
            entry_at=entry_at,
        )
        return {
            "compensated": True,
            "updated_at": projection.updated_at,
        }

    def get_current_parking(self, *, vehicle_num: str) -> dict:
        projection = self.current_location_repository.get_by_vehicle_num(vehicle_num)
        if projection is None:
            raise ParkingQueryProjectionNotFoundError("current parking projection not found")
        return {
            "vehicle_num": projection.vehicle_num,
            "slot_id": projection.slot_id,
            "zone_id": projection.zone_id,
            "slot_type": projection.slot_type,
            "entry_at": projection.entry_at,
            "updated_at": projection.updated_at,
            "slot_code": projection.slot_code or "",
        }

    def get_zone_availability(self, *, slot_type: str) -> dict:
        payload = self.zone_availability_service.get(slot_type=slot_type)
        return {
            "slot_type": payload.get("slotType", slot_type),
            "available_count": payload["availableCount"],
            "updated_at": timezone.now(),
        }

    def _save_projection(
        self,
        *,
        history_id: int,
        vehicle_num: str,
        slot_id: int,
        slot_code: str,
        zone_id: int,
        slot_type: str,
        entry_at: datetime | None,
    ):
        incoming_entry_at = entry_at or timezone.now()
        current_projection = self.current_location_repository.get_by_vehicle_num(vehicle_num)
        if current_projection is not None and self._is_newer_projection(
            current_entry_at=current_projection.entry_at,
            current_history_id=current_projection.history_id,
            incoming_entry_at=incoming_entry_at,
            incoming_history_id=history_id,
        ):
            return current_projection

        return self.current_location_repository.save_projection(
            {
                "vehicle_num": vehicle_num,
                "history_id": history_id,
                "zone_id": zone_id,
                "slot_id": slot_id,
                "slot_code": slot_code,
                "slot_type": slot_type,
                "entry_at": incoming_entry_at,
            }
        )

    @staticmethod
    def _is_newer_projection(
        *,
        current_entry_at,
        current_history_id: int | None,
        incoming_entry_at,
        incoming_history_id: int,
    ) -> bool:
        current_key = (current_entry_at, current_history_id or 0)
        incoming_key = (incoming_entry_at, incoming_history_id)
        return current_key > incoming_key
