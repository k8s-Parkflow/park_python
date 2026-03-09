from __future__ import annotations

from parking_command_service.repositories import (
    DjangoParkingRecordRepository,
    DjangoParkingProjectionWriter,
    DjangoVehicleRepository,
)
from parking_command_service.services import ParkingRecordCommandService


def get_parking_record_command_service() -> ParkingRecordCommandService:
    return ParkingRecordCommandService(
        parking_record_repository=DjangoParkingRecordRepository(),
        projection_writer=DjangoParkingProjectionWriter(),
        vehicle_repository=DjangoVehicleRepository(),
    )
