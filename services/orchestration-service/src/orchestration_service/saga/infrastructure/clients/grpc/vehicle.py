from __future__ import annotations

import os

import grpc

from contracts.gen.python.vehicle.v1 import vehicle_pb2, vehicle_pb2_grpc
from orchestration_service.saga.infrastructure.clients.grpc.base import GrpcClientBase


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

    def get_vehicle(self, *, vehicle_num: str) -> dict:
        stub = self.get_stub(vehicle_pb2_grpc.VehicleServiceStub)
        request = vehicle_pb2.GetVehicleRequest(vehicle_num=vehicle_num)
        response = self.invoke_unary(
            dependency="vehicle-service",
            rpc_call=stub.GetVehicle,
            request=request,
        )
        return {
            "vehicle_num": response.vehicle_num,
            "vehicle_type": response.vehicle_type,
            "active": response.active,
        }


__all__ = ["VehicleGrpcClient"]
