from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class TypedAvailabilityAT(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 등록된 Zone은 모두 전체 여석 합산 대상이다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")
        Zone.objects.create(zone_id=3, zone_name="C")

        # Zone A/B/C의 일반 타입 잔여석은 각각 3대, 4대, 5대다.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=100,
            occupied_count=97,
            available_count=3,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="GENERAL",
            total_count=100,
            occupied_count=96,
            available_count=4,
        )
        ZoneAvailability.objects.create(
            zone_id=3,
            slot_type="GENERAL",
            total_count=100,
            occupied_count=95,
            available_count=5,
        )

        # Zone A/B/C의 전기차 타입 잔여석은 각각 1대, 2대, 2대다.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="EV",
            total_count=100,
            occupied_count=99,
            available_count=1,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="EV",
            total_count=100,
            occupied_count=98,
            available_count=2,
        )
        ZoneAvailability.objects.create(
            zone_id=3,
            slot_type="EV",
            total_count=100,
            occupied_count=98,
            available_count=2,
        )

        # Zone A/B/C의 장애인 타입 잔여석은 각각 1대, 2대, 3대다.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="DISABLED",
            total_count=100,
            occupied_count=99,
            available_count=1,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="DISABLED",
            total_count=100,
            occupied_count=98,
            available_count=2,
        )
        ZoneAvailability.objects.create(
            zone_id=3,
            slot_type="DISABLED",
            total_count=100,
            occupied_count=97,
            available_count=3,
        )

    def test_returns_general_total(self) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=GENERAL"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "GENERAL",
                "availableCount": 12,
            },
        )

    def test_returns_ev_total(self) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=EV"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "EV",
                "availableCount": 5,
            },
        )

    def test_returns_disabled_total(self) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=DISABLED"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "DISABLED",
                "availableCount": 6,
            },
        )

    def test_rejects_invalid_slot_type(self) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=VIP"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {
                        "slot_type": ["지원하지 않는 슬롯 타입입니다."],
                    },
                }
            },
        )

    def test_returns_total_without_slot_type(self) -> None:
        # Given
        request_path = "/api/zones/availabilities"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "availableCount": 23,
            },
        )
