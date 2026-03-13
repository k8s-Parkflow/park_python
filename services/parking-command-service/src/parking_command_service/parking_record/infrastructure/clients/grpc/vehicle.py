from __future__ import annotations

import os

import grpc

from contracts.gen.python.vehicle.v1 import vehicle_pb2, vehicle_pb2_grpc
from parking_command_service.parking_record.infrastructure.clients.grpc.base import (
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
            target=target or os.getenv("VEHICLE_SERVICE_GRPC_TARGET", "127.0.0.1:50015"),
            timeout=timeout,
            channel=channel,
            stub=stub,
        )

    def get_vehicle(self, *, vehicle_num: str) -> dict | None:
        stub = self.get_stub(vehicle_pb2_grpc.VehicleServiceStub)
        request = vehicle_pb2.GetVehicleRequest(vehicle_num=vehicle_num)

        try:
            response = stub.GetVehicle(request, timeout=self.timeout)
        except grpc.RpcError as error:
            if error.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise DownstreamDependencyError(
                message="차량 조회 서비스 호출에 실패했습니다."
            ) from error

        return {
            "vehicle_num": response.vehicle_num,
            "vehicle_type": response.vehicle_type,
            "active": response.active,
        }

    def exists(self, *, vehicle_num: str) -> bool:
        return self.get_vehicle(vehicle_num=vehicle_num) is not None
