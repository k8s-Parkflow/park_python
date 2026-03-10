from __future__ import annotations

from datetime import datetime, timezone

from google.protobuf.timestamp_pb2 import Timestamp

from contracts.gen.python.parking_query.v1 import parking_query_pb2


def timestamp_to_datetime(timestamp: Timestamp) -> datetime | None:
    if timestamp.seconds == 0 and timestamp.nanos == 0:
        return None
    return timestamp.ToDatetime().astimezone(timezone.utc)


def datetime_to_timestamp(value: datetime | None) -> Timestamp:
    timestamp = Timestamp()
    if value is not None:
        timestamp.FromDatetime(value.astimezone(timezone.utc))
    return timestamp


def build_apply_entry_response(*, payload: dict) -> parking_query_pb2.ApplyEntryProjectionResponse:
    return parking_query_pb2.ApplyEntryProjectionResponse(
        projected=payload["projected"],
        updated_at=datetime_to_timestamp(payload["updated_at"]),
    )


def build_apply_exit_response(*, payload: dict) -> parking_query_pb2.ApplyExitProjectionResponse:
    return parking_query_pb2.ApplyExitProjectionResponse(
        projected=payload["projected"],
        updated_at=datetime_to_timestamp(payload["updated_at"]),
    )


def build_compensate_entry_response(
    *,
    payload: dict,
) -> parking_query_pb2.CompensateEntryProjectionResponse:
    return parking_query_pb2.CompensateEntryProjectionResponse(
        compensated=payload["compensated"],
        updated_at=datetime_to_timestamp(payload["updated_at"]),
    )


def build_compensate_exit_response(
    *,
    payload: dict,
) -> parking_query_pb2.CompensateExitProjectionResponse:
    return parking_query_pb2.CompensateExitProjectionResponse(
        compensated=payload["compensated"],
        updated_at=datetime_to_timestamp(payload["updated_at"]),
    )


def build_current_parking_response(*, payload: dict) -> parking_query_pb2.GetCurrentParkingResponse:
    return parking_query_pb2.GetCurrentParkingResponse(
        vehicle_num=payload["vehicle_num"],
        slot_id=payload["slot_id"],
        zone_id=payload["zone_id"],
        slot_type=payload["slot_type"],
        entry_at=datetime_to_timestamp(payload["entry_at"]),
        updated_at=datetime_to_timestamp(payload["updated_at"]),
        slot_code=payload["slot_code"],
        zone_name=payload["zone_name"],
    )


def build_zone_availability_response(
    *,
    payload: dict,
) -> parking_query_pb2.GetZoneAvailabilityResponse:
    return parking_query_pb2.GetZoneAvailabilityResponse(
        slot_type=payload["slot_type"],
        available_count=payload["available_count"],
        updated_at=datetime_to_timestamp(payload["updated_at"]),
    )
