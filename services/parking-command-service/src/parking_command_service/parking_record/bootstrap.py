from __future__ import annotations

from parking_command_service.clients.grpc.parking_query import (
    ParkingQueryGrpcProjectionWriter,
)
from parking_command_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient
from parking_command_service.parking_record.application.command_service import (
    ParkingRecordCommandService,
)
from parking_command_service.parking_record.infrastructure.repositories import (
    DjangoParkingRecordRepository,
)


def get_parking_record_command_service() -> ParkingRecordCommandService:
    return ParkingRecordCommandService(
        parking_record_repository=DjangoParkingRecordRepository(),
        projection_writer=ParkingQueryGrpcProjectionWriter(),
        vehicle_repository=VehicleGrpcClient(),
        zone_policy_gateway=ZoneGrpcClient(),
    )
