from __future__ import annotations

from zone_service.models import ParkingSlot, Zone
from zone_service.repositories.parking_slot import ParkingSlotRepository
from zone_service.repositories.zone import ZoneRepository


def is_vehicle_entry_allowed(*, slot_type_name: str, vehicle_type: str) -> bool:
    return slot_type_name == "GENERAL" or slot_type_name == vehicle_type


def build_validate_entry_policy_payload(*, parking_slot: ParkingSlot, vehicle_type: str) -> dict:
    zone = parking_slot.zone
    slot_type_name = parking_slot.slot_type.type_name
    entry_allowed = (
        parking_slot.is_active
        and zone.is_active
        and is_vehicle_entry_allowed(
            slot_type_name=slot_type_name,
            vehicle_type=vehicle_type,
        )
    )
    return {
        "slot_id": parking_slot.slot_id,
        "zone_id": zone.zone_id,
        "slot_type": slot_type_name,
        "zone_active": zone.is_active,
        "entry_allowed": entry_allowed,
        "zone_name": zone.zone_name,
        "slot_code": parking_slot.slot_code,
    }


class ZonePolicyService:
    def __init__(
        self,
        *,
        parking_slot_repository: ParkingSlotRepository | None = None,
        zone_repository: ZoneRepository | None = None,
    ) -> None:
        self.parking_slot_repository = parking_slot_repository or ParkingSlotRepository()
        self.zone_repository = zone_repository or ZoneRepository()

    def validate_entry_policy(self, *, slot_id: int, vehicle_type: str) -> dict:
        parking_slot = self.parking_slot_repository.get(slot_id=slot_id)
        return build_validate_entry_policy_payload(
            parking_slot=parking_slot,
            vehicle_type=vehicle_type,
        )

    def get_zone(self, *, zone_id: int) -> Zone:
        return self.zone_repository.get(zone_id=zone_id)
