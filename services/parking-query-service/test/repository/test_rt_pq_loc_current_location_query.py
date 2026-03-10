from django.test import TestCase
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView
from park_py.tests.support.current_location import CurrentLocationModuleLoaderMixin


class CurrentLocationRepositoryQueryTests(CurrentLocationModuleLoaderMixin, TestCase):
    def test_should_fetch_location__when_vehicle_num_given(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        repository = repository_module.CurrentLocationRepository()
        CurrentParkingView.objects.create(
            vehicle_num="69가-3455",
            zone_name="A존",
            slot_name="A033",
            slot_type="GENERAL",
            entry_at=timezone.now(),
        )

        # When
        projection = repository.get_by_vehicle_num("69가-3455")

        # Then
        self.assertIsNotNone(projection)
        self.assertEqual(projection.vehicle_num, "69가-3455")
        self.assertEqual(projection.zone_name, "A존")
        self.assertEqual(projection.slot_name, "A033")

    def test_should_return_empty__when_location_missing(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        repository = repository_module.CurrentLocationRepository()

        # When
        projection = repository.get_by_vehicle_num("69가-3455")

        # Then
        self.assertIsNone(projection)
