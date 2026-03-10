from parking_query_service.repositories.current_location_repository import (
    CurrentLocationRepository,
)
from parking_query_service.repositories.vehicle_repository import VehicleRepository
from parking_query_service.services.current_location_service import CurrentLocationService


def build_current_location_service() -> CurrentLocationService:
    return CurrentLocationService(
        current_location_repository=CurrentLocationRepository(),
        vehicle_repository=VehicleRepository(),
    )
