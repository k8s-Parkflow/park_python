from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability


@override_settings(ROOT_URLCONF="park_py.urls")
class MissingTypeTotalAT(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 일부 타입 집계가 비어 있어도 전체 조회는 정상 응답이어야 한다.
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

    def test_returns_total_with_missing_types(self) -> None:
        # Given
        request_path = "/api/zones/availabilities"

        # When
        response = self.client.get(request_path)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "availableCount": 7,
            },
        )
