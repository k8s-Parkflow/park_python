from __future__ import annotations

from contracts.gen.python.zone.v1 import zone_pb2
from zone_service.zone_catalog.domain.entities import Zone


def build_validate_entry_policy_response(*, payload: dict) -> zone_pb2.ValidateEntryPolicyResponse:
    return zone_pb2.ValidateEntryPolicyResponse(
        slot_id=payload["slot_id"],
        zone_id=payload["zone_id"],
        slot_type=payload["slot_type"],
        zone_active=payload["zone_active"],
        entry_allowed=payload["entry_allowed"],
        zone_name=payload["zone_name"],
        slot_code=payload["slot_code"],
    )


def build_get_zone_response(*, zone: Zone) -> zone_pb2.GetZoneResponse:
    return zone_pb2.GetZoneResponse(
        zone_id=zone.zone_id,
        zone_name=zone.zone_name,
        is_active=zone.is_active,
    )
