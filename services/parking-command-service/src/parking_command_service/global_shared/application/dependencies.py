from __future__ import annotations

from parking_command_service.domains.parking_record.application.services import (
    ParkingRecordCommandService,
)
from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingProjectionWriter,
    DjangoParkingRecordRepository,
    DjangoVehicleRepository,
)


def get_parking_record_command_service() -> ParkingRecordCommandService:
    return ParkingRecordCommandService(
        parking_record_repository=DjangoParkingRecordRepository(),
        projection_writer=DjangoParkingProjectionWriter(),
        vehicle_repository=DjangoVehicleRepository(),
    )
