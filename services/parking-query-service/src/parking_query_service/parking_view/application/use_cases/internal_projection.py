from __future__ import annotations

from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_datetime

from park_py.error_handling import ApplicationError, ErrorCode

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


def _claim_operation_record(*, operation_id: str, action: str) -> tuple[ParkingQueryOperation, dict | None]:
    try:
        with transaction.atomic():
            return ParkingQueryOperation.objects.create(
                operation_id=operation_id,
                action=action,
            ), None
    except IntegrityError:
        record = ParkingQueryOperation.objects.select_for_update().get(
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
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="PROJECT_ENTRY",
        )
        if cached_response is not None:
            return cached_response

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
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="REVERT_ENTRY",
        )
        if cached_response is not None:
            return cached_response

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
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="PROJECT_EXIT",
        )
        if cached_response is not None:
            return cached_response

        try:
            projection = CurrentParkingView.objects.get(vehicle_num=vehicle_num)
            availability = ZoneAvailability.objects.get(
                zone_id=projection.zone_id,
                slot_type=projection.slot_type,
            )
            if availability.occupied_count <= 0:
                raise ApplicationError(
                    code=ErrorCode.CONFLICT,
                    status=409,
                    details={
                        "error_code": "projection_count_underflow",
                        "zone_id": projection.zone_id,
                        "slot_type": projection.slot_type,
                    },
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
        record, cached_response = _claim_operation_record(
            operation_id=operation_id,
            action="RESTORE_EXIT",
        )
        if cached_response is not None:
            return cached_response

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
