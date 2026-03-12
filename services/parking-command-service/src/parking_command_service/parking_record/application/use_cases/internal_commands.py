from __future__ import annotations

from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_datetime

from shared.error_handling import ApplicationError, ErrorCode

from parking_command_service.models import ParkingCommandOperation
from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingHistoryStatus
from parking_command_service.models import ParkingSlot
from parking_command_service.models import SlotOccupancy


def _claim_operation_record(*, operation_id: str, action: str) -> tuple[ParkingCommandOperation, dict | None]:
    try:
        with transaction.atomic():
            return ParkingCommandOperation.objects.create(
                operation_id=operation_id,
                action=action,
            ), None
    except IntegrityError:
        record = ParkingCommandOperation.objects.select_for_update().get(
            operation_id=operation_id,
            action=action,
        )
        if record.response_payload is None:
            raise ApplicationError(
                code=ErrorCode.CONFLICT,
                status=409,
                details={
                    "error_code": "operation_in_progress",
                    "operation_id": operation_id,
                    "action": action,
                },
            )
        return record, record.response_payload


def _complete_operation_record(*, record: ParkingCommandOperation, response_payload: dict) -> None:
    record.response_payload = response_payload
    record.save(update_fields=["response_payload", "updated_at"])


def enter_parking(*, operation_id: str, vehicle_num: str, slot_id: int, requested_at: str) -> dict:
    with transaction.atomic():
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="CREATE_ENTRY",
        )
        if cached_response is not None:
            return cached_response

        slot = ParkingSlot.objects.get(slot_id=slot_id)
        occupancy, _ = SlotOccupancy.objects.get_or_create(slot=slot)
        try:
            history = ParkingHistory.start(
                slot=slot,
                vehicle_num=vehicle_num,
                entry_at=parse_datetime(requested_at),
            )
            history.save()
            occupancy.occupy(vehicle_num=vehicle_num, history=history, occupied_at=history.entry_at)
            occupancy.save()
            response = {
                "history_id": history.history_id,
                "slot_id": slot.slot_id,
                "vehicle_num": history.vehicle_num,
                "entry_at": history.entry_at.isoformat(),
                "status": history.status,
            }
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response


def cancel_entry(*, operation_id: str, history_id: int) -> dict:
    with transaction.atomic():
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="CANCEL_ENTRY",
        )
        if cached_response is not None:
            return cached_response

        try:
            history = ParkingHistory.objects.filter(history_id=history_id).select_related("slot").first()
            if history is None:
                response = {"history_id": history_id, "slot_released": True}
            else:
                occupancy = SlotOccupancy.objects.filter(slot=history.slot).first()
                if (
                    occupancy is not None
                    and occupancy.occupied
                    and occupancy.history_id == history.history_id
                ):
                    occupancy.release()
                    occupancy.save()
                history.delete()
                response = {"history_id": history_id, "slot_released": True}
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response


def exit_parking(*, operation_id: str, vehicle_num: str, requested_at: str) -> dict:
    with transaction.atomic():
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="CREATE_EXIT",
        )
        if cached_response is not None:
            return cached_response

        try:
            history = ParkingHistory.objects.get(vehicle_num=vehicle_num, exit_at__isnull=True)
            occupancy = SlotOccupancy.objects.get(slot=history.slot)
            history.exit(exited_at=parse_datetime(requested_at))
            history.save()
            occupancy.release()
            occupancy.save()
            response = {
                "history_id": history.history_id,
                "slot_id": history.slot_id,
                "vehicle_num": history.vehicle_num,
                "exit_at": history.exit_at.isoformat(),
                "status": history.status,
            }
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response


def restore_exit(*, operation_id: str, history_id: int) -> dict:
    with transaction.atomic():
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="RESTORE_EXIT",
        )
        if cached_response is not None:
            return cached_response

        try:
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
            response = {"history_id": history.history_id, "slot_reoccupied": True}
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response
