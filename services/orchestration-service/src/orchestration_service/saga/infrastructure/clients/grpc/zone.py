from __future__ import annotations

import os

import grpc

from contracts.gen.python.zone.v1 import zone_pb2, zone_pb2_grpc
from orchestration_service.saga.infrastructure.clients.grpc.base import GrpcClientBase


class ZoneGrpcClient(GrpcClientBase):
    def __init__(
        self,
        *,
        target: str | None = None,
        timeout: float = 5.0,
        channel: grpc.Channel | None = None,
        stub=None,
    ) -> None:
        super().__init__(
            target=target or os.getenv("ZONE_SERVICE_GRPC_TARGET", "127.0.0.1:50052"),
            timeout=timeout,
            channel=channel,
            stub=stub,
        )

    def validate_entry_policy(self, *, slot_id: int, vehicle_type: str) -> dict:
        stub = self.get_stub(zone_pb2_grpc.ZoneServiceStub)
        request = zone_pb2.ValidateEntryPolicyRequest(
            slot_id=slot_id,
            vehicle_type=vehicle_type,
        )
        response = self.invoke_unary(
            dependency="zone-service",
            rpc_call=stub.ValidateEntryPolicy,
            request=request,
        )
        return {
            "slot_id": response.slot_id,
            "zone_id": response.zone_id,
            "slot_type": response.slot_type,
            "zone_active": response.zone_active,
            "entry_allowed": response.entry_allowed,
            "zone_name": response.zone_name,
            "slot_code": response.slot_code,
        }

    def get_zone(self, *, zone_id: int) -> dict:
        stub = self.get_stub(zone_pb2_grpc.ZoneServiceStub)
        request = zone_pb2.GetZoneRequest(zone_id=zone_id)
        response = self.invoke_unary(
            dependency="zone-service",
            rpc_call=stub.GetZone,
            request=request,
        )
        return {
            "zone_id": response.zone_id,
            "zone_name": response.zone_name,
            "is_active": response.is_active,
        }


__all__ = ["ZoneGrpcClient"]
