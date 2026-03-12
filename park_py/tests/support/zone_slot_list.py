from importlib import import_module
from typing import Any

from django.test import SimpleTestCase
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView
from zone_service.models.parking_slot import ParkingSlot
from zone_service.models.slot_type import SlotType
from zone_service.models.zone import Zone


ZONE_SLOT_LIST_PATH = "/zones"


class ZoneSlotListFixtureMixin:
    def create_zone(self, *, zone_name: str = "A존", is_active: bool = True) -> Zone:
        return Zone.objects.create(zone_name=zone_name, is_active=is_active)

    def create_slot_type(self, *, type_name: str = "GENERAL") -> SlotType:
        return SlotType.objects.create(type_name=type_name)

    def create_zone_slot(
        self,
        *,
        zone: Zone,
        slot_type: SlotType,
        slot_id: int,
        slot_code: str,
        is_active: bool = True,
    ) -> ParkingSlot:
        return ParkingSlot.objects.create(
            slot_id=slot_id,
            zone=zone,
            slot_type=slot_type,
            slot_code=slot_code,
            is_active=is_active,
        )

    def create_current_parking_view(
        self,
        *,
        vehicle_num: str,
        zone_id: int,
        zone_name: str,
        slot_id: int,
        slot_name: str,
        slot_type: str,
        entry_at=None,
    ) -> CurrentParkingView:
        return CurrentParkingView.objects.create(
            vehicle_num=vehicle_num,
            zone_id=zone_id,
            zone_name=zone_name,
            slot_id=slot_id,
            slot_name=slot_name,
            slot_type=slot_type,
            entry_at=entry_at or timezone.now(),
        )

    def request_zone_slots(self, *, zone_id: int):
        return self.client.get(f"{ZONE_SLOT_LIST_PATH}/{zone_id}/slots")


class ZoneSlotListModuleLoaderMixin(SimpleTestCase):
    def load_query_service_module(self):
        try:
            return import_module("parking_query_service.services.zone_slot_query_service")
        except ModuleNotFoundError as exception:
            self.fail(f"zone_slot_query_service module must be implemented: {exception}")

    def load_repository_module(self):
        try:
            return import_module("parking_query_service.repositories.zone_slot_repository")
        except ModuleNotFoundError as exception:
            self.fail(f"zone_slot_repository module must be implemented: {exception}")


class StubZoneSlotRepository:
    def __init__(self, *, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def list_by_zone_id(self, *, zone_id: int) -> list[dict[str, Any]]:
        self.last_zone_id = zone_id
        return self.rows


class StubZoneExistence:
    def __init__(self, *, zone_exists: bool) -> None:
        self._zone_exists = zone_exists

    def exists(self, *, zone_id: int) -> bool:
        self.last_zone_id = zone_id
        return self._zone_exists
