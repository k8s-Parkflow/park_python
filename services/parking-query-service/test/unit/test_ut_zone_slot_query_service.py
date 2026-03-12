from django.test import SimpleTestCase

from park_py.tests.support.zone_slot_list import (
    StubZoneExistence,
    StubZoneSlotRepository,
    ZoneSlotListModuleLoaderMixin,
)


class ZoneSlotQueryServiceUnitTests(ZoneSlotListModuleLoaderMixin, SimpleTestCase):
    def test_should_build_payload__when_rows_loaded(self) -> None:
        # Given
        module = self.load_query_service_module()
        service = module.ZoneSlotQueryService(
            zone_slot_repository=StubZoneSlotRepository(
                rows=[
                    {
                        "slot_id": 11,
                        "slot_name": "A001",
                        "category": "GENERAL",
                        "is_active": True,
                        "vehicle_num": "69가-3455",
                    }
                ]
            ),
            zone_existence=StubZoneExistence(zone_exists=True),
        )

        # When
        payload = service.get_zone_slots(zone_id=1)

        # Then
        self.assertEqual(
            payload,
            {
                "zoneId": 1,
                "slots": [
                    {
                        "slotId": 11,
                        "slot_name": "A001",
                        "category": "GENERAL",
                        "isActive": True,
                        "vehicleNum": "69가-3455",
                    }
                ],
            },
        )

    def test_should_raise_not_found__when_zone_missing(self) -> None:
        # Given
        module = self.load_query_service_module()
        service = module.ZoneSlotQueryService(
            zone_slot_repository=StubZoneSlotRepository(rows=[]),
            zone_existence=StubZoneExistence(zone_exists=False),
        )

        # When / Then
        with self.assertRaises(module.ZoneNotFoundError):
            service.get_zone_slots(zone_id=999)

    def test_should_map_response_fields__when_building_payload(self) -> None:
        # Given
        module = self.load_query_service_module()
        service = module.ZoneSlotQueryService(
            zone_slot_repository=StubZoneSlotRepository(
                rows=[
                    {
                        "slot_id": 12,
                        "slot_name": "A002",
                        "category": "EV",
                        "is_active": False,
                        "vehicle_num": None,
                    }
                ]
            ),
            zone_existence=StubZoneExistence(zone_exists=True),
        )

        # When
        payload = service.get_zone_slots(zone_id=1)

        # Then
        self.assertEqual(
            payload["slots"][0],
            {
                "slotId": 12,
                "slot_name": "A002",
                "category": "EV",
                "isActive": False,
                "vehicleNum": None,
            },
        )

    def test_should_keep_empty_slots__when_vehicle_num_missing(self) -> None:
        # Given
        module = self.load_query_service_module()
        service = module.ZoneSlotQueryService(
            zone_slot_repository=StubZoneSlotRepository(
                rows=[
                    {
                        "slot_id": 13,
                        "slot_name": "A003",
                        "category": "GENERAL",
                        "is_active": True,
                        "vehicle_num": None,
                    }
                ]
            ),
            zone_existence=StubZoneExistence(zone_exists=True),
        )

        # When
        payload = service.get_zone_slots(zone_id=1)

        # Then
        self.assertEqual(len(payload["slots"]), 1)
        self.assertIsNone(payload["slots"][0]["vehicleNum"])
