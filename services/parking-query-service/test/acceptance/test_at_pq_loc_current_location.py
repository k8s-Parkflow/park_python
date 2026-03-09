from django.test import TestCase, override_settings
from django.utils import timezone

from parking_query_service.models.current_parking_view import CurrentParkingView
from vehicle_service.models.enums import VehicleType
from vehicle_service.models.vehicle import Vehicle


@override_settings(ROOT_URLCONF="park_py.urls_test")
class CurrentLocationAcceptanceTests(TestCase):
    def test_should_return_location__when_vehicle_parked(self) -> None:
        # Given
        self._create_vehicle("69가-3455")
        self._create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.client.get("/api/parking/current/69가-3455")

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "vehicle_num": "69가-3455",
                "zone_name": "A존",
                "slot_name": "A033",
            },
        )

    def test_should_return_location__when_vehicle_num_normalized(self) -> None:
        # Given
        self._create_vehicle("69가-3455")
        self._create_current_location("69가-3455", "A존", "A033")

        # When
        response = self.client.get("/api/parking/current/69가3455")

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "vehicle_num": "69가-3455",
                "zone_name": "A존",
                "slot_name": "A033",
            },
        )

    def test_should_return_bad_request__when_vehicle_num_invalid(self) -> None:
        # Given
        invalid_vehicle_num = "invalid!"

        # When
        response = self.client.get(f"/api/parking/current/{invalid_vehicle_num}")

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"vehicle_num": ["지원하지 않는 차량 번호 형식입니다."]},
                }
            },
        )

    def test_should_return_not_found__when_vehicle_not_parked(self) -> None:
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

    def test_should_return_not_found__when_vehicle_missing(self) -> None:
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

    def test_should_return_latest_location__when_location_updated(self) -> None:
        # Given
        self._create_vehicle("69가-3455")
        CurrentParkingView.objects.create(
            vehicle_num="69가-3455",
            zone_name="A존",
            slot_name="A033",
            slot_type="GENERAL",
            entry_at=timezone.now(),
        )
        CurrentParkingView.objects.filter(vehicle_num="69가-3455").update(
            zone_name="B존",
            slot_name="B101",
            updated_at=timezone.now(),
        )

        # When
        response = self.client.get("/api/parking/current/69가-3455")

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "vehicle_num": "69가-3455",
                "zone_name": "B존",
                "slot_name": "B101",
            },
        )

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
