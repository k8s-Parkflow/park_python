from django.test import TestCase, override_settings

from park_py.tests.support.current_location import CurrentLocationFixtureMixin


@override_settings(ROOT_URLCONF="park_py.urls_test")
class CurrentLocationValidationContractTests(CurrentLocationFixtureMixin, TestCase):
    def test_should_preserve_bad_request__when_vehicle_num_invalid(self) -> None:
        # Given
        invalid_vehicle_num = "invalid!"

        # When
        response = self.request_current_location(invalid_vehicle_num)

        # Then
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "bad_request")
        self.assertEqual(payload["error"]["message"], "잘못된 요청입니다.")
        self.assertIn("vehicle_num", payload["error"]["details"])
        self.assertIsInstance(payload["error"]["details"]["vehicle_num"], list)


@override_settings(ROOT_URLCONF="park_py.urls_test")
class CurrentLocationNotFoundContractTests(CurrentLocationFixtureMixin, TestCase):
    def test_should_preserve_not_found__when_vehicle_not_parked(self) -> None:
        # Given
        self.create_vehicle("69가-3455")

        # When
        response = self.request_current_location("69가-3455")

        # Then
        self.assert_not_found_message(response, "현재 주차 중인 차량이 없습니다.")

    def test_should_preserve_not_found__when_vehicle_missing(self) -> None:
        # Given
        missing_vehicle_num = "11가-1111"

        # When
        response = self.request_current_location(missing_vehicle_num)

        # Then
        self.assert_not_found_message(response, "존재하지 않는 차량입니다.")
