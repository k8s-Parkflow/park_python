from datetime import timedelta

from django.test import SimpleTestCase
from django.utils import timezone

from park_py.tests.support.current_location import (
    CurrentLocationModuleLoaderMixin,
    StubProjectionWriter,
)


class CurrentLocationProjectionServiceUnitTests(CurrentLocationModuleLoaderMixin, SimpleTestCase):
    def test_should_sync_location_projection__when_projection_applied(self) -> None:
        # Given
        module = self.load_projection_service_module()
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
        module = self.load_projection_service_module()
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
