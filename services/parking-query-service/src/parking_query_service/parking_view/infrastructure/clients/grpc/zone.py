from __future__ import annotations

import os

import grpc

from contracts.gen.python.zone.v1 import zone_pb2, zone_pb2_grpc
from parking_query_service.parking_view.infrastructure.clients.grpc.base import (
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

    def exists_by_zone_id(self, zone_id: int) -> bool:
        stub = self.get_stub(zone_pb2_grpc.ZoneServiceStub)
        request = zone_pb2.GetZoneRequest(zone_id=zone_id)

        try:
            stub.GetZone(request, timeout=self.timeout)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise DownstreamDependencyError(
                message="존 조회 서비스 호출에 실패했습니다."
            ) from error

        return True

    def get_zone_slots(self, *, zone_id: int) -> list[dict]:
        stub = self.get_stub(zone_pb2_grpc.ZoneServiceStub)
        request = zone_pb2.GetZoneSlotsRequest(zone_id=zone_id)

        try:
            response = stub.GetZoneSlots(request, timeout=self.timeout)
        except grpc.RpcError as error:
            raise DownstreamDependencyError(
                message="존 슬롯 조회 서비스 호출에 실패했습니다."
            ) from error

        return [
            {
                "slot_id": slot.slot_id,
                "slot_name": slot.slot_code,
                "category": slot.slot_type,
                "is_active": slot.is_active,
            }
            for slot in response.slots
        ]
