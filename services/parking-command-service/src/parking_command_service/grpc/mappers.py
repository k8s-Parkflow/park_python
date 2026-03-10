from __future__ import annotations

from datetime import datetime, timezone

from google.protobuf.timestamp_pb2 import Timestamp

from contracts.gen.python.parking_command.v1 import parking_command_pb2


def timestamp_to_datetime(timestamp: Timestamp) -> datetime | None:
    if timestamp.seconds == 0 and timestamp.nanos == 0:
        return None
    return timestamp.ToDatetime().astimezone(timezone.utc)


def datetime_to_timestamp(value: datetime | None) -> Timestamp:
    timestamp = Timestamp()
    if value is not None:
        timestamp.FromDatetime(value.astimezone(timezone.utc))
    return timestamp


def build_create_entry_response(*, snapshot) -> parking_command_pb2.CreateEntryResponse:
    return parking_command_pb2.CreateEntryResponse(
        history_id=snapshot.history_id,
        slot_id=snapshot.slot_id,
        vehicle_num=snapshot.vehicle_num,
        entry_at=datetime_to_timestamp(snapshot.entry_at),
        status=snapshot.status,
    )


def build_compensate_entry_response(*, payload: dict) -> parking_command_pb2.CompensateEntryResponse:
    return parking_command_pb2.CompensateEntryResponse(
        history_id=payload["history_id"],
        slot_released=payload["slot_released"],
        compensated_at=datetime_to_timestamp(payload["compensated_at"]),
    )
