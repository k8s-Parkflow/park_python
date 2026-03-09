from datetime import timedelta
from importlib import import_module
from typing import Any, Dict, Optional

from django.test import SimpleTestCase
from django.utils import timezone


class CurrentLocationUnitTests(SimpleTestCase):
    def test_should_normalize_vehicle_num__when_formatted(self) -> None:
        # Given
        module = self._load_query_service_module()

        # When
        normalized = module.normalize_vehicle_num("69가-3455 ")

        # Then
        self.assertEqual(normalized, "69가3455")

    def test_should_build_location__when_projection_found(self) -> None:
        # Given
        module = self._load_query_service_module()
        current_location_repository = StubCurrentLocationRepository(
            projection={
                "vehicle_num": "69가-3455",
                "zone_name": "A존",
                "slot_name": "A033",
            }
        )
        vehicle_repository = StubVehicleRepository(exists=True)
        service = module.CurrentLocationService(
            current_location_repository=current_location_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        location = service.get_current_location("69가-3455")

        # Then
        self.assertEqual(
            location,
            {
                "vehicle_num": "69가-3455",
                "zone_name": "A존",
                "slot_name": "A033",
            },
        )

    def test_should_raise_not_parked__when_location_missing(self) -> None:
        # Given
        module = self._load_query_service_module()
        service = module.CurrentLocationService(
            current_location_repository=StubCurrentLocationRepository(projection=None),
            vehicle_repository=StubVehicleRepository(exists=True),
        )

        # When / Then
        with self.assertRaises(module.CurrentVehicleNotParkedError):
            service.get_current_location("69가-3455")

    def test_should_raise_vehicle_not_found__when_vehicle_missing(self) -> None:
        # Given
        module = self._load_query_service_module()
        service = module.CurrentLocationService(
            current_location_repository=StubCurrentLocationRepository(projection=None),
            vehicle_repository=StubVehicleRepository(exists=False),
        )

        # When / Then
        with self.assertRaises(module.VehicleNotFoundError):
            service.get_current_location("69가-3455")

    def test_should_sync_location_projection__when_projection_applied(self) -> None:
        # Given
        module = self._load_projection_service_module()
        repository = StubProjectionWriter()
        service = module.CurrentLocationProjectionService(
            current_location_repository=repository,
        )
        first_updated_at = timezone.now()
        second_updated_at = first_updated_at + timedelta(minutes=5)

        # When
        service.upsert_current_location(
            {
                "vehicle_num": "69가-3455",
                "zone_name": "A존",
                "slot_name": "A033",
                "slot_type": "GENERAL",
                "entry_at": first_updated_at,
                "updated_at": first_updated_at,
            }
        )
        service.upsert_current_location(
            {
                "vehicle_num": "69가-3455",
                "zone_name": "B존",
                "slot_name": "B101",
                "slot_type": "GENERAL",
                "entry_at": first_updated_at,
                "updated_at": second_updated_at,
            }
        )
        latest_projection = repository.get_by_vehicle_num("69가-3455")
        service.remove_current_location("69가-3455", second_updated_at + timedelta(minutes=1))

        # Then
        self.assertEqual(latest_projection["zone_name"], "B존")
        self.assertEqual(latest_projection["slot_name"], "B101")
        self.assertIsNone(repository.get_by_vehicle_num("69가-3455"))

    def test_should_ignore_stale_update__when_event_older(self) -> None:
        # Given
        module = self._load_projection_service_module()
        repository = StubProjectionWriter()
        service = module.CurrentLocationProjectionService(
            current_location_repository=repository,
        )
        latest_updated_at = timezone.now()
        stale_updated_at = latest_updated_at - timedelta(minutes=5)
        repository.save(
            {
                "vehicle_num": "69가-3455",
                "zone_name": "B존",
                "slot_name": "B101",
                "slot_type": "GENERAL",
                "entry_at": latest_updated_at,
                "updated_at": latest_updated_at,
            }
        )

        # When
        service.upsert_current_location(
            {
                "vehicle_num": "69가-3455",
                "zone_name": "A존",
                "slot_name": "A033",
                "slot_type": "GENERAL",
                "entry_at": stale_updated_at,
                "updated_at": stale_updated_at,
            }
        )

        # Then
        projection = repository.get_by_vehicle_num("69가-3455")
        self.assertEqual(projection["zone_name"], "B존")
        self.assertEqual(projection["slot_name"], "B101")

    def _load_query_service_module(self):
        try:
            return import_module("parking_query_service.services.current_location_service")
        except ModuleNotFoundError as exception:
            self.fail(f"current_location_service module must be implemented: {exception}")

    def _load_projection_service_module(self):
        try:
            return import_module("parking_query_service.services.current_location_projection_service")
        except ModuleNotFoundError as exception:
            self.fail(f"current_location_projection_service module must be implemented: {exception}")


class StubCurrentLocationRepository:
    def __init__(self, projection: Optional[Dict[str, Any]]) -> None:
        self.projection = projection
        self.last_vehicle_num: Optional[str] = None

    def get_by_vehicle_num(self, vehicle_num: str) -> Optional[Dict[str, Any]]:
        self.last_vehicle_num = vehicle_num
        return self.projection


class StubVehicleRepository:
    def __init__(self, exists: bool) -> None:
        self.exists = exists
        self.last_vehicle_num: Optional[str] = None

    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        self.last_vehicle_num = vehicle_num
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
