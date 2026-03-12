from __future__ import annotations

from django.db.models import F

from zone_service.zone_catalog.domain.entities import ParkingSlot


class ParkingSlotRepository:
    def get(self, *, slot_id: int) -> ParkingSlot:
        return ParkingSlot.objects.select_related("zone", "slot_type").get(slot_id=slot_id)

    def list_by_zone_id(self, *, zone_id: int):
        return (
            ParkingSlot.objects.select_related("slot_type")
            .filter(zone_id=zone_id)
            .annotate(slot_type_name=F("slot_type__type_name"))
            .order_by("slot_code", "slot_id")
        )

    def list_all(self):
        return (
            ParkingSlot.objects.select_related("zone", "slot_type")
            .annotate(slot_type_name=F("slot_type__type_name"))
            .order_by("zone_id", "slot_code", "slot_id")
        )
