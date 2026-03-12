from __future__ import annotations

from contracts.gen.python.vehicle.v1 import vehicle_pb2
from vehicle_service.vehicle.domain.entities import Vehicle


def build_get_vehicle_response(*, vehicle: Vehicle) -> vehicle_pb2.GetVehicleResponse:
    return vehicle_pb2.GetVehicleResponse(
        vehicle_num=vehicle.vehicle_num,
        vehicle_type=vehicle.vehicle_type,
        active=True,
    )
