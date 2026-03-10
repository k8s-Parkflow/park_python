from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability


@override_settings(ROOT_URLCONF="park_py.urls")
class SlotTypeNormalizationCT(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 혼합 대소문자 입력도 표준 응답 계약을 유지해야 한다.
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

    def test_typed_schema_with_mixed_case_slot_type(self) -> None:
        response = self.client.get("/api/zones/availabilities?slot_type=dIsAbLeD")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "DISABLED")
        self.assertEqual(payload["availableCount"], 6)
