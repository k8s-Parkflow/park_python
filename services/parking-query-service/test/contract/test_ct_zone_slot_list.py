from django.test import TestCase, override_settings

from park_py.tests.support.zone_slot_list import ZoneSlotListFixtureMixin


@override_settings(ROOT_URLCONF="park_py.urls_test")
class ZoneSlotListContractTests(ZoneSlotListFixtureMixin, TestCase):
    def test_should_match_zone_slot_schema__when_success(self) -> None:
        # Given
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        self.create_current_parking_view(
            vehicle_num="69가-3455",
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            slot_id=11,
            slot_name="A001",
            slot_type="GENERAL",
        )

        # When
        response = self.request_zone_slots(zone_id=zone.zone_id)

        # Then
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"zoneId", "slots"})
        self.assertEqual(payload["zoneId"], zone.zone_id)
        self.assertIsInstance(payload["slots"], list)
        self.assertEqual(len(payload["slots"]), 1)
        slot = payload["slots"][0]
        self.assertEqual(
            set(slot.keys()),
            {"slotId", "slot_name", "category", "isActive", "vehicleNum"},
        )
        self.assertIsInstance(slot["slotId"], int)
        self.assertIsInstance(slot["slot_name"], str)
        self.assertIsInstance(slot["category"], str)
        self.assertIsInstance(slot["isActive"], bool)
        self.assertIsInstance(slot["vehicleNum"], str)

    def test_should_match_empty_schema__when_zone_has_no_slots(self) -> None:
        # Given
        zone = self.create_zone(zone_name="B존")

        # When
        response = self.request_zone_slots(zone_id=zone.zone_id)

        # Then
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"zoneId", "slots"})
        self.assertEqual(payload["zoneId"], zone.zone_id)
        self.assertEqual(payload["slots"], [])

    def test_should_preserve_not_found__when_zone_missing(self) -> None:
        # Given
        missing_zone_id = 999

        # When
        response = self.request_zone_slots(zone_id=missing_zone_id)

        # Then
        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertEqual(set(payload.keys()), {"error"})
        self.assertEqual(set(payload["error"].keys()), {"code", "message"})
        self.assertEqual(payload["error"]["code"], "not_found")
        self.assertEqual(payload["error"]["message"], "존을 찾을 수 없습니다.")
