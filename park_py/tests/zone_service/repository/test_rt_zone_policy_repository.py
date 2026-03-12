from __future__ import annotations

from django.test import TestCase

from zone_service.models import ParkingSlot, SlotType, Zone
from zone_service.repositories.parking_slot import ParkingSlotRepository


class ZonePolicyRepositoryTests(TestCase):
    databases = "__all__"

    def test_should_return_slot_with_zone_and_slot_type__when_slot_exists(self) -> None:
        """[RT-ZONE-GRPC-01] 슬롯 조회 저장소"""

        # Given
        zone = Zone.objects.create(zone_name="A-1", is_active=True)
        slot_type = SlotType.objects.create(type_name="GENERAL")
        ParkingSlot.objects.create(
            slot_id=7,
            zone=zone,
            slot_type=slot_type,
            slot_code="A001",
            is_active=True,
        )

        # When
        parking_slot = ParkingSlotRepository().get(slot_id=7)

        # Then
        self.assertEqual(parking_slot.slot_id, 7)
        self.assertEqual(parking_slot.zone.zone_name, "A-1")
        self.assertEqual(parking_slot.slot_type.type_name, "GENERAL")
        self.assertEqual(parking_slot.slot_code, "A001")
