from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability


@override_settings(ROOT_URLCONF="park_py.urls")
class MissingTypeTotalCT(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 전체 조회 시 일부 타입 집계가 없어도 단일 필드 응답 계약을 유지해야 한다.
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

    def test_total_schema_with_missing_types(self) -> None:
        response = self.client.get("/api/zones/availabilities")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"availableCount"})
        self.assertEqual(payload["availableCount"], 7)
