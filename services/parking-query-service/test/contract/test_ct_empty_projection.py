from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class EmptyProjectionCT(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # EV 집계가 없어도 타입별 응답 계약은 유지되어야 한다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")

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

    def test_typed_schema_with_empty_projection(self) -> None:
        response = self.client.get("/api/zones/availabilities?slot_type=EV")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "EV")
        self.assertEqual(payload["availableCount"], 0)
