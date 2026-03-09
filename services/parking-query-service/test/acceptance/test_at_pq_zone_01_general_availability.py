from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class ZoneGeneralAvailabilityAcceptanceTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 등록된 Zone은 모두 전체 여석 합산 대상이다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")
        Zone.objects.create(zone_id=3, zone_name="C")

        # Zone A의 일반 타입 잔여석은 3대
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=100,
            occupied_count=97,
            available_count=3,
        )

        # Zone B의 일반 타입 잔여석은 4대
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="GENERAL",
            total_count=100,
            occupied_count=96,
            available_count=4,
        )

        # Zone C의 일반 타입 잔여석은 5대다.
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

    def test_should_return_total_general_available_count_for_all_zones__when_general_slot_type_requested(
        self,
    ) -> None:
        # Given (전체 Zone의 일반 타입 잔여석 합계를 조회)
        request_path = "/api/zones/availabilities?slot_type=GENERAL"

        # When
        response = self.client.get(request_path)

        # Then
        # Zone A(3) + Zone B(4) + Zone C(5)가 합산되어 2가 반환되어야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "GENERAL",
                "availableCount": 12,
            },
        )

    def test_should_return_total_ev_available_count_for_all_zones__when_ev_slot_type_requested(
        self,
    ) -> None:
        # Given (전체 Zone의 전기차 타입 잔여석 합계를 조회)
        request_path = "/api/zones/availabilities?slot_type=EV"

        # When
        response = self.client.get(request_path)

        # Then
        # Zone A(1) + Zone B(2) + Zone C(2)이 합산되어 5가 반환되어야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "EV",
                "availableCount": 5,
            },
        )

    def test_should_return_total_disabled_available_count_for_all_zones__when_disabled_slot_type_requested(
        self,
    ) -> None:
        # Given (전체 Zone의 장애인 타입 잔여석 합계를 조회)
        request_path = "/api/zones/availabilities?slot_type=DISABLED"

        # When
        response = self.client.get(request_path)

        # Then
        # Zone A(1) + Zone B(2) + Zone C(3)이 합산되어 6이 반환되어야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "DISABLED",
                "availableCount": 6,
            },
        )
