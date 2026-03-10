from __future__ import annotations

from parking_command_service.domains.parking_record.domain import (
    ParkingHistory,
    ParkingSlot,
    SlotOccupancy,
)


class DjangoParkingRecordRepository:
    def get_slot_for_update(self, *, slot_id: int) -> ParkingSlot | None:
        return ParkingSlot.objects.select_for_update().filter(slot_id=slot_id).first()

    def get_slot_by_identity_for_update(self, *, zone_id: int, slot_code: str) -> ParkingSlot | None:
        return (
            ParkingSlot.objects.select_for_update()
            .filter(zone_id=zone_id, slot_code=slot_code)
            .first()
        )

    def get_or_create_occupancy_for_update(self, *, slot: ParkingSlot) -> SlotOccupancy:
        SlotOccupancy.objects.get_or_create(slot=slot)
        return SlotOccupancy.objects.select_for_update().get(slot=slot)

    def has_active_history_for_vehicle(self, *, vehicle_num: str) -> bool:
        return ParkingHistory.objects.select_for_update().filter(
            vehicle_num=vehicle_num,
            exit_at__isnull=True,
        ).exists()

    def get_active_history_for_vehicle_for_update(self, *, vehicle_num: str) -> ParkingHistory | None:
        return (
            ParkingHistory.objects.select_for_update()
            .select_related("slot")
            .filter(vehicle_num=vehicle_num, exit_at__isnull=True)
            .first()
        )

    def save_history(self, *, history: ParkingHistory) -> ParkingHistory:
        history.full_clean()
        history.save()
        return history

    def save_occupancy(self, *, occupancy: SlotOccupancy) -> SlotOccupancy:
        occupancy.full_clean()
        occupancy.save()
        return occupancy
