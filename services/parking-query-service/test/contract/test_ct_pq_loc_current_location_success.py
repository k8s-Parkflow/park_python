from django.test import TestCase, override_settings

from park_py.tests.support.current_location import CurrentLocationFixtureMixin


@override_settings(ROOT_URLCONF="park_py.urls_test")
class CurrentLocationSuccessContractTests(CurrentLocationFixtureMixin, TestCase):
    def test_should_match_location_schema__when_found(self) -> None:
        # Given
        self.create_vehicle("69가-3455")
        self.create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.request_current_location("69가-3455")

        # Then
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"vehicle_num", "zone_name", "slot_name"})
        self.assertIsInstance(payload["vehicle_num"], str)
        self.assertIsInstance(payload["zone_name"], str)
        self.assertIsInstance(payload["slot_name"], str)

    def test_should_match_location_schema__when_vehicle_num_normalized(self) -> None:
        # Given
        self.create_vehicle("69가-3455")
        self.create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.request_current_location("69가3455")

        # Then
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"vehicle_num", "zone_name", "slot_name"})
