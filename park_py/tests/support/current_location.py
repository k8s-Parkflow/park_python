from importlib import import_module
from typing import Any, Dict, Optional
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView
from parking_query_service.repositories.current_location_repository import CurrentLocationRepository
from parking_query_service.services.current_location_service import CurrentLocationService
from park_py.tests.grpc_support import build_direct_stub
from vehicle_service.models.enums import VehicleType
from vehicle_service.grpc.servicers import VehicleGrpcServicer
from vehicle_service.models.vehicle import Vehicle


CURRENT_LOCATION_PATH = "/api/parking/current"


class CurrentLocationFixtureMixin:
    def create_vehicle(self, vehicle_num: str) -> Vehicle:
        return Vehicle.objects.create(
            vehicle_num=vehicle_num,
            vehicle_type=VehicleType.General,
        )

    def create_current_location(
        self,
        vehicle_num: str,
        zone_name: str,
        slot_name: str,
    ) -> CurrentParkingView:
        return CurrentParkingView.objects.create(
            vehicle_num=vehicle_num,
            zone_name=zone_name,
            slot_name=slot_name,
            slot_type="GENERAL",
            entry_at=timezone.now(),
        )

    def request_current_location(self, vehicle_num: str):
        with patch(
            "parking_query_service.views.build_current_location_service",
            return_value=self.build_current_location_service(),
        ):
            return self.client.get(f"{CURRENT_LOCATION_PATH}/{vehicle_num}")

    def build_current_location_service(self) -> CurrentLocationService:
        client_module = import_module("parking_query_service.clients.grpc.vehicle")
        return CurrentLocationService(
            current_location_repository=CurrentLocationRepository(),
            vehicle_lookup=client_module.VehicleGrpcClient(
                stub=build_direct_stub(
                    servicer=VehicleGrpcServicer(),
                    method_names=["GetVehicle"],
                )
            ),
        )

    def assert_location_payload(
        self,
        response,
        *,
        vehicle_num: str,
        zone_name: str,
        slot_name: str,
    ) -> None:
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "vehicle_num": vehicle_num,
                "zone_name": zone_name,
                "slot_name": slot_name,
            },
        )

    def assert_not_found_message(self, response, message: str) -> None:
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "not_found",
                    "message": message,
                }
            },
        )


class CurrentLocationModuleLoaderMixin(SimpleTestCase):
    def load_query_service_module(self):
        try:
            return import_module("parking_query_service.services.current_location_service")
        except ModuleNotFoundError as exception:
            self.fail(f"current_location_service module must be implemented: {exception}")

    def load_projection_service_module(self):
        try:
            return import_module("parking_query_service.services.current_location_projection_service")
        except ModuleNotFoundError as exception:
            self.fail(f"current_location_projection_service module must be implemented: {exception}")

    def load_repository_module(self):
        try:
            return import_module("parking_query_service.repositories.current_location_repository")
        except ModuleNotFoundError as exception:
            self.fail(f"current_location_repository module must be implemented: {exception}")


class StubCurrentLocationRepository:
    def __init__(self, projection: Optional[Dict[str, Any]]) -> None:
        self.projection = projection

    def get_by_vehicle_num(self, _vehicle_num: str) -> Optional[Dict[str, Any]]:
        return self.projection


class StubVehicleLookup:
    def __init__(self, exists: bool) -> None:
        self.exists = exists

    def exists_by_vehicle_num(self, _vehicle_num: str) -> bool:
        return self.exists


class StubProjectionWriter:
    def __init__(self) -> None:
        self.storage: Dict[str, Dict[str, Any]] = {}

    def get_by_vehicle_num(self, vehicle_num: str) -> Optional[Dict[str, Any]]:
        return self.storage.get(vehicle_num)

    def save(self, projection: Dict[str, Any]) -> None:
        self.storage[projection["vehicle_num"]] = projection

    def delete_by_vehicle_num(self, vehicle_num: str) -> None:
        self.storage.pop(vehicle_num, None)
