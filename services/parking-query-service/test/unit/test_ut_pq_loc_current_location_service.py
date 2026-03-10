from django.test import SimpleTestCase

from park_py.tests.support.current_location import (
    CurrentLocationModuleLoaderMixin,
    StubCurrentLocationRepository,
    StubVehicleLookup,
)


class CurrentLocationServiceUnitTests(CurrentLocationModuleLoaderMixin, SimpleTestCase):
    def test_should_build_location__when_projection_found(self) -> None:
        # Given
        module = self.load_query_service_module()
        service = module.CurrentLocationService(
            current_location_repository=StubCurrentLocationRepository(
                projection={
                    "vehicle_num": "69가-3455",
                    "zone_name": "A존",
                    "slot_name": "A033",
                }
            ),
            vehicle_lookup=StubVehicleLookup(exists=True),
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
        module = self.load_query_service_module()
        service = module.CurrentLocationService(
            current_location_repository=StubCurrentLocationRepository(projection=None),
            vehicle_lookup=StubVehicleLookup(exists=True),
        )

        # When / Then
        with self.assertRaises(module.CurrentVehicleNotParkedError):
            service.get_current_location("69가-3455")

    def test_should_raise_vehicle_not_found__when_vehicle_missing(self) -> None:
        # Given
        module = self.load_query_service_module()
        service = module.CurrentLocationService(
            current_location_repository=StubCurrentLocationRepository(projection=None),
            vehicle_lookup=StubVehicleLookup(exists=False),
        )

        # When / Then
        with self.assertRaises(module.VehicleNotFoundError):
            service.get_current_location("69가-3455")
