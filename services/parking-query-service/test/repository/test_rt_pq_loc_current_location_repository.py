from importlib import import_module

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView


class CurrentLocationRepositoryTests(TestCase):
    def test_should_fail_on_duplicate_vehicle_num__when_saving_location(self) -> None:
        # Given
        CurrentParkingView.objects.create(
            vehicle_num="69가-3455",
            zone_name="A존",
            slot_name="A033",
            slot_type="GENERAL",
            entry_at=timezone.now(),
        )

        # When / Then
        with self.assertRaises(IntegrityError):
            CurrentParkingView.objects.create(
                vehicle_num="69가-3455",
                zone_name="B존",
                slot_name="B101",
                slot_type="GENERAL",
                entry_at=timezone.now(),
            )

    def test_should_fetch_location__when_vehicle_num_given(self) -> None:
        # Given
        repository_module = self._load_repository_module()
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
        repository_module = self._load_repository_module()
        repository = repository_module.CurrentLocationRepository()

        # When
        projection = repository.get_by_vehicle_num("69가-3455")

        # Then
        self.assertIsNone(projection)

    def _load_repository_module(self):
        try:
            return import_module("parking_query_service.repositories.current_location_repository")
        except ModuleNotFoundError as exception:
            self.fail(f"current_location_repository module must be implemented: {exception}")
