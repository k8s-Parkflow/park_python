from __future__ import annotations

from typing import TypedDict

from django.db.models import F, OuterRef, Subquery

from parking_query_service.models.current_parking_view import CurrentParkingView
from zone_service.models.zone import Zone
from zone_service.models.parking_slot import ParkingSlot


class ZoneSlotRow(TypedDict):
    slot_id: int
    slot_name: str
    category: str
    is_active: bool
    vehicle_num: str | None


class ZoneExistenceRepository:
    def exists(self, *, zone_id: int) -> bool:
        return Zone.objects.filter(zone_id=zone_id).exists()


class ZoneSlotRepository:
    def list_by_zone_id(self, *, zone_id: int) -> list[ZoneSlotRow]:
        return list(self._zone_slots_queryset(zone_id=zone_id))

    def _zone_slots_queryset(self, *, zone_id: int):
        latest_vehicle_num = (
            CurrentParkingView.objects.filter(slot_id=OuterRef("slot_id"))
            .order_by("-entry_at", "-updated_at")
            .values("vehicle_num")[:1]
        )

        return (
            ParkingSlot.objects.select_related("slot_type")
            .filter(zone_id=zone_id)
            .annotate(
                slot_name=F("slot_code"),
                category=F("slot_type__type_name"),
            )
            .annotate(vehicle_num=Subquery(latest_vehicle_num))
            .order_by("slot_code", "slot_id")
            .values("slot_id", "slot_name", "category", "is_active", "vehicle_num")
        )
