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

    def test_should_return_bad_request__when_unsupported_slot_type_requested(
        self,
    ) -> None:
        # Given (지원하지 않는 타입으로 전체 Zone 여석 조회를 요청)
        request_path = "/api/zones/availabilities?slot_type=VIP"

        # When
        response = self.client.get(request_path)

        # Then
        # API는 표준 오류 포맷의 400 bad_request를 반환해야 한다.
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

    def test_should_return_total_available_count_for_all_slot_types__when_slot_type_not_provided(
        self,
    ) -> None:
        # Given (전체 Zone의 전체 타입 잔여석 합계 조회)
        request_path = "/api/zones/availabilities"

        # When
        response = self.client.get(request_path)

        # Then
        # GENERAL(12) + EV(5) + DISABLED(6)이 합산된 23이 반환되어야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "availableCount": 23,
            },
        )


@override_settings(ROOT_URLCONF="park_py.urls")
class ZoneTypedAvailabilityWithoutProjectionAcceptanceTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 전체 Zone은 존재하지만 EV 타입 집계 데이터는 비어 있다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")

        # GENERAL 타입만 존재해도 EV 조회는 정상 응답으로 0을 반환해야 한다.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=7,
            available_count=3,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=6,
            available_count=4,
        )

    def test_should_return_zero_available_count__when_supported_slot_type_has_no_projection(
        self,
    ) -> None:
        # Given (지원하는 타입이지만 EV 집계 데이터가 없다)
        request_path = "/api/zones/availabilities?slot_type=EV"

        # When
        response = self.client.get(request_path)

        # Then
        # 집계가 없더라도 오류가 아니라 0으로 응답해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "EV",
                "availableCount": 0,
            },
        )


@override_settings(ROOT_URLCONF="park_py.urls")
class ZoneTotalAvailabilityWithMissingTypesAcceptanceTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 일부 타입 집계가 비어 있어도 전체 조회는 정상 응답이어야 한다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")

        # GENERAL 집계만 존재하고 EV, DISABLED는 비어 있는 상태를 만든다.
        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=7,
            available_count=3,
        )
        ZoneAvailability.objects.create(
            zone_id=2,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=6,
            available_count=4,
        )

    def test_should_return_total_available_count__when_some_slot_types_have_no_projection(
        self,
    ) -> None:
        # Given (EV, DISABLED 집계는 없고 GENERAL만 존재)
        request_path = "/api/zones/availabilities"

        # When
        response = self.client.get(request_path)

        # Then
        # 누락된 타입은 0으로 보고 GENERAL 합계 7만 반환해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "availableCount": 7,
            },
        )


@override_settings(ROOT_URLCONF="park_py.urls")
class ZoneTypedAvailabilityNormalizationAcceptanceTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 대소문자가 섞인 입력도 지원 타입으로 정규화되어야 한다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")
        Zone.objects.create(zone_id=3, zone_name="C")

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

    def test_should_return_normalized_slot_type__when_slot_type_requested_with_mixed_case(
        self,
    ) -> None:
        # Given (지원 타입을 혼합 대소문자로 전달)
        request_path = "/api/zones/availabilities?slot_type=GeNeRaL"

        # When
        response = self.client.get(request_path)

        # Then
        # 입력값은 GENERAL로 정규화되어 정상 응답해야 한다.
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "slotType": "GENERAL",
                "availableCount": 12,
            },
        )
