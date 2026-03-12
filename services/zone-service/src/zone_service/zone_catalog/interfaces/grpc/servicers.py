from __future__ import annotations

import grpc

from contracts.gen.python.zone.v1 import zone_pb2_grpc
from zone_service.zone_catalog.interfaces.grpc.mappers import (
    build_get_zone_slots_response,
    build_get_zone_response,
    build_validate_entry_policy_response,
)
from zone_service.zone_catalog.domain.entities import ParkingSlot, Zone
from zone_service.zone_catalog.domain.policies import ZonePolicyService


class ZoneGrpcServicer(zone_pb2_grpc.ZoneServiceServicer):
    def __init__(self, *, zone_policy_service: ZonePolicyService | None = None) -> None:
        self.zone_policy_service = zone_policy_service or ZonePolicyService()

    def ValidateEntryPolicy(self, request, context):  # noqa: N802
        try:
            payload = self.zone_policy_service.validate_entry_policy(
                slot_id=request.slot_id,
                vehicle_type=request.vehicle_type,
            )
        except ParkingSlot.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "parking slot not found")

        return build_validate_entry_policy_response(payload=payload)

    def GetZone(self, request, context):  # noqa: N802
        try:
            zone = self.zone_policy_service.get_zone(zone_id=request.zone_id)
        except Zone.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "zone not found")

        return build_get_zone_response(zone=zone)

    def GetZoneSlots(self, request, context):  # noqa: N802
        try:
            slots = self.zone_policy_service.get_zone_slots(zone_id=request.zone_id)
        except Zone.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "zone not found")

        return build_get_zone_slots_response(zone_id=request.zone_id, slots=slots)
