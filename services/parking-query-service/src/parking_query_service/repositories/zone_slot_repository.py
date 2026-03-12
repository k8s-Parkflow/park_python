from __future__ import annotations

from typing import TypedDict

from django.db.models import F

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
        slots = list(self._zone_slots_queryset(zone_id=zone_id))
        if not slots:
            return []

        vehicle_nums_by_slot_id = self._load_vehicle_nums_by_slot_id(
            slot_ids=[slot["slot_id"] for slot in slots]
        )

        return [
            {
                **slot,
                "vehicle_num": vehicle_nums_by_slot_id.get(slot["slot_id"]),
            }
            for slot in slots
        ]

    def _zone_slots_queryset(self, *, zone_id: int):
        return (
            ParkingSlot.objects.select_related("slot_type")
            .filter(zone_id=zone_id)
            .annotate(
                slot_name=F("slot_code"),
                category=F("slot_type__type_name"),
            )
            .order_by("slot_code", "slot_id")
            .values("slot_id", "slot_name", "category", "is_active")
        )

    def _load_vehicle_nums_by_slot_id(self, *, slot_ids: list[int]) -> dict[int, str]:
        rows = (
            CurrentParkingView.objects.filter(slot_id__in=slot_ids)
            .order_by("slot_id", "-entry_at", "-updated_at")
            .values("slot_id", "vehicle_num")
        )

        latest_vehicle_nums: dict[int, str] = {}
        for row in rows:
            latest_vehicle_nums.setdefault(row["slot_id"], row["vehicle_num"])

        return latest_vehicle_nums
