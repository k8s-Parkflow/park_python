from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class EmptyProjectionAT(TestCase):

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

    def test_returns_zero_for_missing_ev(self) -> None:
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
                "availableCount": 0,
            },
        )
