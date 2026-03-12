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
from parking_query_service.clients.grpc.zone import ZoneGrpcClient
from parking_query_service.repositories.zone_slot_repository import (
    ZoneExistenceRepository,
    ZoneSlotRepository,
)
from parking_query_service.services.zone_slot_query_service import ZoneSlotQueryService


def build_get_current_location() -> CurrentLocationService:
    return CurrentLocationService(
        current_location_repository=CurrentLocationRepository(),
        vehicle_lookup=VehicleGrpcClient(),
    )


def build_get_zone_availability() -> ZoneAvailabilityService:
    return ZoneAvailabilityService(
        zone_availability_repository=ZoneAvailabilityRepository(),
    )


def build_zone_slot_query_service() -> ZoneSlotQueryService:
    zone_client = ZoneGrpcClient()
    return ZoneSlotQueryService(
        zone_slot_repository=ZoneSlotRepository(zone_client=zone_client),
        zone_existence=ZoneExistenceRepository(zone_client=zone_client),
    )
