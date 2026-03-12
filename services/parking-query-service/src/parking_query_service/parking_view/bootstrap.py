from parking_query_service.parking_view.application.use_cases.get_current_location import (
    CurrentLocationService,
)
from parking_query_service.parking_view.application.use_cases.get_zone_availability import (
    ZoneAvailabilityService,
)
from parking_query_service.parking_view.infrastructure.clients.grpc.vehicle import (
    VehicleGrpcClient,
)
from parking_query_service.parking_view.infrastructure.persistence.repositories.current_location_repository import (
    CurrentLocationRepository,
)
from parking_query_service.parking_view.infrastructure.persistence.repositories.zone_availability_repository import (
    ZoneAvailabilityRepository,
)


def build_get_current_location() -> CurrentLocationService:
    return CurrentLocationService(
        current_location_repository=CurrentLocationRepository(),
        vehicle_lookup=VehicleGrpcClient(),
    )


def build_get_zone_availability() -> ZoneAvailabilityService:
    return ZoneAvailabilityService(
        zone_availability_repository=ZoneAvailabilityRepository(),
    )
