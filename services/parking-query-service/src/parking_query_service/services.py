from __future__ import annotations

from django.db import transaction
from django.utils.dateparse import parse_datetime

from parking_query_service.models import CurrentParkingView
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


def project_entry(
    *,
    vehicle_num: str,
    slot_id: int,
    zone_id: int,
    slot_type: str,
    entry_at: str,
) -> dict:
    with transaction.atomic():
        availability = ZoneAvailability.objects.get(zone_id=zone_id, slot_type=slot_type)
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
        return {"projected": True}


def revert_entry(*, vehicle_num: str) -> dict:
    with transaction.atomic():
        projection = CurrentParkingView.objects.filter(vehicle_num=vehicle_num).first()
        if projection is None:
            return {"reverted": True}

        availability = ZoneAvailability.objects.filter(
            zone_id=projection.zone_id,
            slot_type=projection.slot_type,
        ).first()
        projection.delete()
        if availability is not None and availability.occupied_count > 0:
            availability.occupied_count -= 1
            availability.available_count += 1
            availability.save(update_fields=["occupied_count", "available_count", "updated_at"])
        return {"reverted": True}


def project_exit(*, vehicle_num: str) -> dict:
    with transaction.atomic():
        projection = CurrentParkingView.objects.get(vehicle_num=vehicle_num)
        availability = ZoneAvailability.objects.get(
            zone_id=projection.zone_id,
            slot_type=projection.slot_type,
        )
        projection.delete()
        availability.occupied_count -= 1
        availability.available_count += 1
        availability.save(update_fields=["occupied_count", "available_count", "updated_at"])
        return {"projected": True}


def restore_exit(
    *,
    vehicle_num: str,
    slot_id: int,
    zone_id: int,
    slot_type: str,
    entry_at: str,
) -> dict:
    with transaction.atomic():
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
        return {"restored": True}

