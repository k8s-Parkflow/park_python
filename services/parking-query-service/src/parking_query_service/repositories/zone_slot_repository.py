from __future__ import annotations

from django.db.models import OuterRef, Subquery

from parking_query_service.models.current_parking_view import CurrentParkingView
from zone_service.models.zone import Zone
from zone_service.models.parking_slot import ParkingSlot


class ZoneExistenceRepository:
    def exists(self, *, zone_id: int) -> bool:
        return Zone.objects.filter(zone_id=zone_id).exists()


class ZoneSlotRepository:
    def list_by_zone_id(self, *, zone_id: int) -> list[dict]:
        latest_vehicle_num = (
            CurrentParkingView.objects.filter(slot_id=OuterRef("slot_id"))
            .order_by("-entry_at", "-updated_at")
            .values("vehicle_num")[:1]
        )
        queryset = (
            ParkingSlot.objects.select_related("slot_type")
            .filter(zone_id=zone_id)
            .annotate(vehicle_num=Subquery(latest_vehicle_num))
            .order_by("slot_code", "slot_id")
        )
        return [
            {
                "slot_id": slot.slot_id,
                "slot_name": slot.slot_code,
                "category": slot.slot_type.type_name,
                "is_active": slot.is_active,
                "vehicle_num": slot.vehicle_num,
            }
            for slot in queryset
        ]
