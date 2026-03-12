from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from park_py.tests.grpc_support import build_direct_stub
from parking_command_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.domains.parking_record.domain import ParkingSlot as CommandParkingSlot
from zone_service.models import ParkingSlot as ZoneParkingSlot
from zone_service.models import SlotType, Zone
from zone_service.zone_catalog.interfaces.grpc.servicers import ZoneGrpcServicer


class SlotLockAnchorSyncRepositoryTests(TestCase):
    databases = "__all__"

    def test_should_create_lock_anchor_rows__when_zone_slots_exist(self) -> None:
        stdout = StringIO()
        zone = Zone.objects.using("zone").create(zone_id=1, zone_name="A존", is_active=True)
        slot_type = SlotType.objects.using("zone").create(slot_type_id=1, type_name="GENERAL")
        ZoneParkingSlot.objects.using("zone").create(
            slot_id=101,
            zone=zone,
            slot_type=slot_type,
            slot_code="A101",
            is_active=True,
        )

        with patch(
            "parking_command_service.management.commands.sync_slot_lock_anchors.ZoneGrpcClient",
            return_value=self._build_zone_client(),
        ):
            call_command("sync_slot_lock_anchors", stdout=stdout)

        anchor = CommandParkingSlot.objects.using("parking_command").get(slot_id=101)
        self.assertEqual(anchor.zone_id, 1)
        self.assertEqual(anchor.slot_code, "A101")
        self.assertTrue(anchor.is_active)
        self.assertIn("synced 1 slot lock anchors", stdout.getvalue())

    def test_should_update_existing_lock_anchor_rows__when_zone_metadata_changes(self) -> None:
        stdout = StringIO()
        zone = Zone.objects.using("zone").create(zone_id=2, zone_name="B존", is_active=True)
        slot_type = SlotType.objects.using("zone").create(slot_type_id=2, type_name="EV")
        ZoneParkingSlot.objects.using("zone").create(
            slot_id=202,
            zone=zone,
            slot_type=slot_type,
            slot_code="B201",
            is_active=True,
        )
        CommandParkingSlot.objects.using("parking_command").create(
            slot_id=202,
            zone_id=99,
            slot_code="OLD",
            is_active=False,
        )

        with patch(
            "parking_command_service.management.commands.sync_slot_lock_anchors.ZoneGrpcClient",
            return_value=self._build_zone_client(),
        ):
            call_command("sync_slot_lock_anchors", stdout=stdout)

        anchor = CommandParkingSlot.objects.using("parking_command").get(slot_id=202)
        self.assertEqual(anchor.zone_id, 2)
        self.assertEqual(anchor.slot_code, "B201")
        self.assertTrue(anchor.is_active)
        self.assertIn("synced 1 slot lock anchors", stdout.getvalue())

    def _build_zone_client(self) -> ZoneGrpcClient:
        return ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["ListParkingSlots"],
            )
        )
