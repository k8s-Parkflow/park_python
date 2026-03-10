from __future__ import annotations

from django.db import transaction
from django.utils.dateparse import parse_datetime

from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ParkingQueryOperation
from parking_query_service.models import ZoneAvailability


def get_current_parking(*, vehicle_num: str) -> dict:
    projection = CurrentParkingView.objects.get(vehicle_num=vehicle_num)
    return {
        "vehicle_num": projection.vehicle_num,
        "slot_id": projection.slot_id,
        "zone_id": projection.zone_id,
        "slot_type": projection.slot_type,
        "entry_at": projection.entry_at.isoformat(),
    }


def _find_cached_response(*, operation_id: str, action: str) -> dict | None:
    record = ParkingQueryOperation.objects.filter(
        operation_id=operation_id,
        action=action,
    ).first()
    if record is None:
        return None
    return record.response_payload


def _create_operation_record(*, operation_id: str, action: str) -> ParkingQueryOperation:
    return ParkingQueryOperation.objects.create(
        operation_id=operation_id,
        action=action,
    )


def _complete_operation_record(*, record: ParkingQueryOperation, response_payload: dict) -> None:
    record.response_payload = response_payload
    record.save(update_fields=["response_payload", "updated_at"])


def project_entry(
    *,
    operation_id: str,
    vehicle_num: str,
    slot_id: int,
    zone_id: int,
    slot_type: str,
    entry_at: str,
) -> dict:
    with transaction.atomic():
        cached_response = _find_cached_response(operation_id=operation_id, action="PROJECT_ENTRY")
        if cached_response is not None:
            return cached_response

        record = _create_operation_record(operation_id=operation_id, action="PROJECT_ENTRY")
        availability = ZoneAvailability.objects.get(zone_id=zone_id, slot_type=slot_type)
        try:
            CurrentParkingView.objects.update_or_create(
                vehicle_num=vehicle_num,
                defaults={
                    "slot_id": slot_id,
                    "zone_id": zone_id,
                    "slot_type": slot_type,
                    "entry_at": parse_datetime(entry_at),
                },
            )
            availability.occupied_count += 1
            availability.available_count -= 1
            availability.save(update_fields=["occupied_count", "available_count", "updated_at"])
            response = {"projected": True}
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response


def revert_entry(*, operation_id: str, vehicle_num: str) -> dict:
    with transaction.atomic():
        cached_response = _find_cached_response(operation_id=operation_id, action="REVERT_ENTRY")
        if cached_response is not None:
            return cached_response

        record = _create_operation_record(operation_id=operation_id, action="REVERT_ENTRY")
        try:
            projection = CurrentParkingView.objects.filter(vehicle_num=vehicle_num).first()
            if projection is None:
                response = {"reverted": True}
            else:
                availability = ZoneAvailability.objects.filter(
                    zone_id=projection.zone_id,
                    slot_type=projection.slot_type,
                ).first()
                projection.delete()
                if availability is not None and availability.occupied_count > 0:
                    availability.occupied_count -= 1
                    availability.available_count += 1
                    availability.save(update_fields=["occupied_count", "available_count", "updated_at"])
                response = {"reverted": True}
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response


def project_exit(*, operation_id: str, vehicle_num: str) -> dict:
    with transaction.atomic():
        cached_response = _find_cached_response(operation_id=operation_id, action="PROJECT_EXIT")
        if cached_response is not None:
            return cached_response

        record = _create_operation_record(operation_id=operation_id, action="PROJECT_EXIT")
        try:
            projection = CurrentParkingView.objects.get(vehicle_num=vehicle_num)
            availability = ZoneAvailability.objects.get(
                zone_id=projection.zone_id,
                slot_type=projection.slot_type,
            )
            projection.delete()
            availability.occupied_count -= 1
            availability.available_count += 1
            availability.save(update_fields=["occupied_count", "available_count", "updated_at"])
            response = {"projected": True}
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response


def restore_exit(
    *,
    operation_id: str,
    vehicle_num: str,
    slot_id: int,
    zone_id: int,
    slot_type: str,
    entry_at: str,
) -> dict:
    with transaction.atomic():
        cached_response = _find_cached_response(operation_id=operation_id, action="RESTORE_EXIT")
        if cached_response is not None:
            return cached_response

        record = _create_operation_record(operation_id=operation_id, action="RESTORE_EXIT")
        try:
            CurrentParkingView.objects.update_or_create(
                vehicle_num=vehicle_num,
                defaults={
                    "slot_id": slot_id,
                    "zone_id": zone_id,
                    "slot_type": slot_type,
                    "entry_at": parse_datetime(entry_at),
                },
            )
            availability = ZoneAvailability.objects.get(zone_id=zone_id, slot_type=slot_type)
            availability.occupied_count += 1
            availability.available_count -= 1
            availability.save(update_fields=["occupied_count", "available_count", "updated_at"])
            response = {"restored": True}
        except Exception:
            record.delete()
            raise

        _complete_operation_record(record=record, response_payload=response)
        return response
