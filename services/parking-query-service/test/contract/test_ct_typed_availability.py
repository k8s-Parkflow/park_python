from django.test import TestCase, override_settings

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


@override_settings(ROOT_URLCONF="park_py.urls")
class TypedAvailabilityCT(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # 등록된 Zone은 모두 전체 타입 여석 합산 대상이다.
        Zone.objects.create(zone_id=1, zone_name="A")
        Zone.objects.create(zone_id=2, zone_name="B")
        Zone.objects.create(zone_id=3, zone_name="C")

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
            total_count=8,
            occupied_count=4,
            available_count=4,
        )
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

    def test_general_schema(self) -> None:
        response = self.client.get("/api/zones/availabilities?slot_type=GENERAL")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "GENERAL")
        self.assertIsInstance(payload["availableCount"], int)

    def test_ev_schema(self) -> None:
        response = self.client.get("/api/zones/availabilities?slot_type=EV")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "EV")
        self.assertIsInstance(payload["availableCount"], int)

    def test_disabled_schema(self) -> None:
        response = self.client.get("/api/zones/availabilities?slot_type=DISABLED")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"slotType", "availableCount"})
        self.assertEqual(payload["slotType"], "DISABLED")
        self.assertIsInstance(payload["availableCount"], int)

    def test_invalid_type_error_schema(self) -> None:
        response = self.client.get("/api/zones/availabilities?slot_type=VIP")
        payload = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(payload.keys()), {"error"})
        self.assertEqual(set(payload["error"].keys()), {"code", "message", "details"})
        self.assertEqual(payload["error"]["code"], "bad_request")
        self.assertEqual(payload["error"]["message"], "잘못된 요청입니다.")
        self.assertEqual(
            payload["error"]["details"],
            {"slot_type": ["지원하지 않는 슬롯 타입입니다."]},
        )

    def test_total_schema_without_slot_type(self) -> None:
        response = self.client.get("/api/zones/availabilities")
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(payload.keys()), {"availableCount"})
        self.assertIsInstance(payload["availableCount"], int)
