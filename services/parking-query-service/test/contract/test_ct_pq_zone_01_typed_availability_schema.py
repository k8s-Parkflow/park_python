from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class ZoneTypedAvailabilityContractTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 등록된 Zone은 모두 전체 타입 여석 합산 대상이다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")
        Zone.objects.create(zone_id=3, zone_name="C")

        # Zone A의 일반 타입 잔여석 3대.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=7,
            available_count=3,
        )

        # Zone B의 일반 타입 잔여석 4대.
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="GENERAL",
            total_count=8,
            occupied_count=4,
            available_count=4,
        )

        # Zone C의 일반 타입 잔여석 5대.
        ZoneAvailability.objects.create(
            zone_id=3,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=5,
            available_count=5,
        )

        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="EV",
            total_count=100,
            occupied_count=90,
            available_count=10,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="EV",
            total_count=100,
            occupied_count=80,
            available_count=20,
        )
        ZoneAvailability.objects.create(
            zone_id=3,
            slot_type="EV",
            total_count=100,
            occupied_count=70,
            available_count=30,
        )

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

    def test_should_match_total_typed_availability_response_schema__when_general_slot_type_requested(
        self,
    ) -> None:

        # Given
        # API는 Zone별 목록이 아니라 전체 Zone 기준 타입 합산 결과만 반환해야 한다.
        request_path = "/api/zones/availabilities?slot_type=GENERAL"

        # When
        response = self.client.get(request_path)

        # Then
        # 응답 계약은 slotType과 availableCount 두 필드만 가진다.
        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "GENERAL")
        self.assertIsInstance(payload["availableCount"], int)

    def test_should_match_total_typed_availability_response_schema__when_ev_slot_type_requested(
        self,
    ) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=EV"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "EV")
        self.assertIsInstance(payload["availableCount"], int)

    def test_should_match_total_typed_availability_response_schema__when_disabled_slot_type_requested(
        self,
    ) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=DISABLED"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "DISABLED")
        self.assertIsInstance(payload["availableCount"], int)

    def test_should_preserve_bad_request_error_contract__when_slot_type_invalid(
        self,
    ) -> None:
        # Given
        # 지원하지 않는 타입 요청은 표준 오류 응답 계약을 유지해야 한다.
        request_path = "/api/zones/availabilities?slot_type=VIP"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 400)

        payload = response.json()

        self.assertEqual(set(payload.keys()), {"error"})
        self.assertEqual(
            set(payload["error"].keys()),
            {"code", "message", "details"},
        )
        self.assertEqual(payload["error"]["code"], "bad_request")
        self.assertEqual(payload["error"]["message"], "잘못된 요청입니다.")
        self.assertEqual(
            payload["error"]["details"],
            {"slot_type": ["지원하지 않는 슬롯 타입입니다."]},
        )

    def test_should_match_total_availability_response_schema__when_slot_type_not_provided(
        self,
    ) -> None:
        # Given
        # slot_type이 없으면 전체 타입 합산 결과만 반환
        request_path = "/api/zones/availabilities"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(set(payload.keys()), {"availableCount"})
        self.assertIsInstance(payload["availableCount"], int)
