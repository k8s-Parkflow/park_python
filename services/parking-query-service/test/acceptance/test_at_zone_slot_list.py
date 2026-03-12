from django.test import TestCase, override_settings

from park_py.tests.support.zone_slot_list import ZoneSlotListFixtureMixin


@override_settings(ROOT_URLCONF="park_py.urls_test")
class ZoneSlotListAcceptanceTests(ZoneSlotListFixtureMixin, TestCase):
    databases = "__all__"

    def test_should_return_zone_slots__when_zone_exists(self) -> None:
        # Given
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        ev = self.create_slot_type(type_name="EV")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        self.create_zone_slot(zone=zone, slot_type=ev, slot_id=12, slot_code="A002", is_active=False)
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
        self.assertJSONEqual(
            response.content,
            {
                "zoneId": zone.zone_id,
                "slots": [
                    {
                        "slotId": 11,
                        "slot_name": "A001",
                        "category": "GENERAL",
                        "isActive": True,
                        "vehicleNum": "69가-3455",
                    },
                    {
                        "slotId": 12,
                        "slot_name": "A002",
                        "category": "EV",
                        "isActive": False,
                        "vehicleNum": None,
                    },
                ],
            },
        )

    def test_should_return_empty_slots__when_zone_has_no_slots(self) -> None:
        # Given
        zone = self.create_zone(zone_name="B존")

        # When
        response = self.request_zone_slots(zone_id=zone.zone_id)

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"zoneId": zone.zone_id, "slots": []})

    def test_should_return_not_found__when_zone_missing(self) -> None:
        # Given
        missing_zone_id = 999

        # When
        response = self.request_zone_slots(zone_id=missing_zone_id)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "not_found",
                    "message": "존을 찾을 수 없습니다.",
                }
            },
        )
