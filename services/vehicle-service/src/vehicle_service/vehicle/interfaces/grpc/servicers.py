from __future__ import annotations

import grpc

from contracts.gen.python.vehicle.v1 import vehicle_pb2_grpc
from vehicle_service.vehicle.application.use_cases.get_vehicle import VehicleLookupService
from vehicle_service.vehicle.domain.entities import Vehicle
from vehicle_service.vehicle.interfaces.grpc.mappers import build_get_vehicle_response


class VehicleGrpcServicer(vehicle_pb2_grpc.VehicleServiceServicer):
    def __init__(self, *, lookup_service: VehicleLookupService | None = None) -> None:
        self.lookup_service = lookup_service or VehicleLookupService()

    def GetVehicle(self, request, context):  # noqa: N802
        try:
            vehicle = self.lookup_service.get_vehicle(vehicle_num=request.vehicle_num)
        except Vehicle.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "vehicle not found")

        return build_get_vehicle_response(vehicle=vehicle)
