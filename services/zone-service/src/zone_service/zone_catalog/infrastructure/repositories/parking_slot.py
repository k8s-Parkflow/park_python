from __future__ import annotations

from zone_service.zone_catalog.domain.entities import ParkingSlot


class ParkingSlotRepository:
    def get(self, *, slot_id: int) -> ParkingSlot:
        return ParkingSlot.objects.select_related("zone", "slot_type").get(slot_id=slot_id)
