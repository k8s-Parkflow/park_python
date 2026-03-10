from __future__ import annotations

from django.db import transaction
from django.utils.dateparse import parse_datetime

from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingHistoryStatus
from parking_command_service.models import ParkingSlot
from parking_command_service.models import SlotOccupancy


def enter_parking(*, vehicle_num: str, slot_id: int, requested_at: str) -> dict:
    with transaction.atomic():
        slot = ParkingSlot.objects.get(slot_id=slot_id)
        occupancy, _ = SlotOccupancy.objects.get_or_create(slot=slot)
        history = ParkingHistory.start(
            slot=slot,
            vehicle_num=vehicle_num,
            entry_at=parse_datetime(requested_at),
        )
        history.save()
        occupancy.occupy(vehicle_num=vehicle_num, history=history, occupied_at=history.entry_at)
        occupancy.save()
        return {
            "history_id": history.history_id,
            "slot_id": slot.slot_id,
            "vehicle_num": history.vehicle_num,
            "entry_at": history.entry_at.isoformat(),
            "status": history.status,
        }


def cancel_entry(*, history_id: int) -> dict:
    with transaction.atomic():
        history = ParkingHistory.objects.filter(history_id=history_id).select_related("slot").first()
        if history is None:
            return {"history_id": history_id, "slot_released": True}

        occupancy = SlotOccupancy.objects.filter(slot=history.slot).first()
        if occupancy is not None and occupancy.occupied:
            occupancy.release()
            occupancy.save()
        history.delete()
        return {"history_id": history_id, "slot_released": True}


def exit_parking(*, vehicle_num: str, requested_at: str) -> dict:
    with transaction.atomic():
        history = ParkingHistory.objects.get(vehicle_num=vehicle_num, exit_at__isnull=True)
        occupancy = SlotOccupancy.objects.get(slot=history.slot)
        history.exit(exited_at=parse_datetime(requested_at))
        history.save()
        occupancy.release()
        occupancy.save()
        return {
            "history_id": history.history_id,
            "slot_id": history.slot_id,
            "vehicle_num": history.vehicle_num,
            "exit_at": history.exit_at.isoformat(),
            "status": history.status,
        }


def restore_exit(*, history_id: int) -> dict:
    with transaction.atomic():
        history = ParkingHistory.objects.get(history_id=history_id)
        occupancy, _ = SlotOccupancy.objects.get_or_create(slot=history.slot)
        history.status = ParkingHistoryStatus.PARKED
        history.exit_at = None
        history.save(update_fields=["status", "exit_at", "updated_at"])
        if not occupancy.occupied:
            occupancy.occupy(
                vehicle_num=history.vehicle_num,
                history=history,
                occupied_at=history.entry_at,
            )
            occupancy.save()
        return {"history_id": history.history_id, "slot_reoccupied": True}

