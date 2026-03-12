from __future__ import annotations

import os

import grpc

from contracts.gen.python.zone.v1 import zone_pb2, zone_pb2_grpc
from parking_command_service.parking_record.infrastructure.clients.grpc.base import (
    DownstreamDependencyError,
    GrpcClientBase,
)


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

    def validate_entry_policy(self, *, slot_id: int, vehicle_type: str) -> dict | None:
        stub = self.get_stub(zone_pb2_grpc.ZoneServiceStub)
        request = zone_pb2.ValidateEntryPolicyRequest(
            slot_id=slot_id,
            vehicle_type=vehicle_type,
        )

        try:
            response = stub.ValidateEntryPolicy(request, timeout=self.timeout)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise DownstreamDependencyError(
                message="구역 정책 서비스 호출에 실패했습니다."
            ) from error

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

        try:
            response = stub.GetZone(request, timeout=self.timeout)
        except grpc.RpcError as error:
            raise DownstreamDependencyError(
                message="구역 조회 서비스 호출에 실패했습니다."
            ) from error

        return {
            "zone_id": response.zone_id,
            "zone_name": response.zone_name,
            "is_active": response.is_active,
        }
