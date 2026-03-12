from parking_command_service.parking_record.application.command_service import (
    ParkingRecordCommandService,
)
from parking_command_service.parking_record.bootstrap import (
    get_parking_record_command_service as _get_parking_record_command_service,
)


def get_parking_record_command_service() -> ParkingRecordCommandService:
    return _get_parking_record_command_service()
