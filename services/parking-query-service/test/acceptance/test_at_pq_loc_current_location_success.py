from django.test import TestCase, override_settings
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView
from park_py.tests.support.current_location import CurrentLocationFixtureMixin


@override_settings(ROOT_URLCONF="park_py.urls_test")
class CurrentLocationSuccessAcceptanceTests(CurrentLocationFixtureMixin, TestCase):
    def test_should_return_location__when_vehicle_parked(self) -> None:
        # Given
        self.create_vehicle("69가-3455")
        self.create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.request_current_location("69가-3455")

        # Then
        self.assert_location_payload(
            response,
            vehicle_num="69가-3455",
            zone_name="A존",
            slot_name="A033",
        )

    def test_should_return_location__when_vehicle_num_normalized(self) -> None:
        # Given
        self.create_vehicle("69가-3455")
        self.create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.request_current_location("69가3455")

        # Then
        self.assert_location_payload(
            response,
            vehicle_num="69가-3455",
            zone_name="A존",
            slot_name="A033",
        )

    def test_should_return_latest_location__when_location_updated(self) -> None:
        # Given
        self.create_vehicle("69가-3455")
        self.create_current_location("69가-3455", "A존", "A033")
        CurrentParkingView.objects.filter(vehicle_num="69가-3455").update(
            zone_name="B존",
            slot_name="B101",
            updated_at=timezone.now(),
        )

        # When
        response = self.request_current_location("69가-3455")

        # Then
        self.assert_location_payload(
            response,
            vehicle_num="69가-3455",
            zone_name="B존",
            slot_name="B101",
        )
