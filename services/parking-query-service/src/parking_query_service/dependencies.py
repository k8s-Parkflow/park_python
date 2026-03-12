from parking_query_service.clients.grpc.vehicle import VehicleGrpcClient
from parking_query_service.repositories.current_location_repository import (
    CurrentLocationRepository,
)
from parking_query_service.repositories.zone_slot_repository import (
    ZoneExistenceRepository,
    ZoneSlotRepository,
)
from parking_query_service.services.current_location_service import CurrentLocationService
from parking_query_service.services.zone_slot_query_service import ZoneSlotQueryService


def build_current_location_service() -> CurrentLocationService:
    return CurrentLocationService(
        current_location_repository=CurrentLocationRepository(),
        vehicle_lookup=VehicleGrpcClient(),
    )


def build_zone_slot_query_service() -> ZoneSlotQueryService:
    return ZoneSlotQueryService(
        zone_slot_repository=ZoneSlotRepository(),
        zone_existence=ZoneExistenceRepository(),
    )
