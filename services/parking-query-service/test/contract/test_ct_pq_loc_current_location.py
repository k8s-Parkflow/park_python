import json

from django.test import TestCase, override_settings
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView
from vehicle_service.models.enums import VehicleType
from vehicle_service.models.vehicle import Vehicle


@override_settings(ROOT_URLCONF="park_py.urls_test")
class CurrentLocationContractTests(TestCase):
    def test_should_match_location_schema__when_found(self) -> None:
        # Given
        self._create_vehicle("69가-3455")
        self._create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.client.get("/api/parking/current/69가-3455")

        # Then
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"vehicle_num", "zone_name", "slot_name"})
        self.assertIsInstance(payload["vehicle_num"], str)
        self.assertIsInstance(payload["zone_name"], str)
        self.assertIsInstance(payload["slot_name"], str)

    def test_should_preserve_bad_request__when_vehicle_num_invalid(self) -> None:
        # Given
        invalid_vehicle_num = "invalid!"

        # When
        response = self.client.get(f"/api/parking/current/{invalid_vehicle_num}")

        # Then
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertEqual(payload["error"]["code"], "bad_request")
        self.assertEqual(payload["error"]["message"], "잘못된 요청입니다.")
        self.assertIn("vehicle_num", payload["error"]["details"])
        self.assertIsInstance(payload["error"]["details"]["vehicle_num"], list)

    def test_should_preserve_not_found__when_vehicle_not_parked(self) -> None:
        # Given
        self._create_vehicle("69가-3455")

        # When
        response = self.client.get("/api/parking/current/69가-3455")

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "not_found",
                    "message": "현재 주차 중인 차량이 없습니다.",
                }
            },
        )

    def test_should_preserve_not_found__when_vehicle_missing(self) -> None:
        # Given
        missing_vehicle_num = "11가-1111"

        # When
        response = self.client.get(f"/api/parking/current/{missing_vehicle_num}")

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "not_found",
                    "message": "존재하지 않는 차량입니다.",
                }
            },
        )

    def test_should_match_location_schema__when_vehicle_num_normalized(self) -> None:
        # Given
        self._create_vehicle("69가-3455")
        self._create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.client.get("/api/parking/current/69가3455")

        # Then
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(set(payload.keys()), {"vehicle_num", "zone_name", "slot_name"})

    def _create_vehicle(self, vehicle_num: str) -> Vehicle:
        return Vehicle.objects.create(
            vehicle_num=vehicle_num,
            vehicle_type=VehicleType.General,
        )

    def _create_current_location(
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
