from __future__ import annotations

import os

import grpc

from contracts.gen.python.vehicle.v1 import vehicle_pb2, vehicle_pb2_grpc
from parking_query_service.parking_view.infrastructure.clients.grpc.base import (
    DownstreamDependencyError,
    GrpcClientBase,
)


class VehicleGrpcClient(GrpcClientBase):
    def __init__(
        self,
        *,
        target: str | None = None,
        timeout: float = 5.0,
        channel: grpc.Channel | None = None,
        stub=None,
    ) -> None:
        super().__init__(
            target=target or os.getenv("VEHICLE_SERVICE_GRPC_TARGET", "127.0.0.1:50051"),
            timeout=timeout,
            channel=channel,
            stub=stub,
        )

    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        stub = self.get_stub(vehicle_pb2_grpc.VehicleServiceStub)
        request = vehicle_pb2.GetVehicleRequest(vehicle_num=vehicle_num)

        try:
            stub.GetVehicle(request, timeout=self.timeout)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise DownstreamDependencyError(
                message="차량 조회 서비스 호출에 실패했습니다."
            ) from error

        return True
