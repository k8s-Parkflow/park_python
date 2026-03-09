from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class SlotTypeNormalizationAT(TestCase):

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

    def test_normalizes_mixed_case_slot_type(self) -> None:
        # Given
        request_path = "/api/zones/availabilities?slot_type=GeNeRaL"

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
