from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView


class CurrentParkingViewConstraintTests(TestCase):
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
