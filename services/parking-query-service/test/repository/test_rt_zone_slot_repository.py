from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from park_py.tests.grpc_support import build_direct_stub
from park_py.tests.support.zone_slot_list import (
    ZoneSlotListFixtureMixin,
    ZoneSlotListModuleLoaderMixin,
)
from zone_service.zone_catalog.interfaces.grpc.servicers import ZoneGrpcServicer


class ZoneSlotRepositoryTests(
    ZoneSlotListFixtureMixin,
    ZoneSlotListModuleLoaderMixin,
    TestCase,
):
    databases = "__all__"

    def test_should_load_slot_rows__when_zone_requested(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        ev = self.create_slot_type(type_name="EV")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        self.create_zone_slot(zone=zone, slot_type=ev, slot_id=12, slot_code="A002", is_active=False)
        repository = repository_module.ZoneSlotRepository(
            zone_client=self._build_zone_client(module=repository_module),
        )

        # When
        rows = repository.list_by_zone_id(zone_id=zone.zone_id)

        # Then
        self.assertEqual(
            rows,
            [
                {
                    "slot_id": 11,
                    "slot_name": "A001",
                    "category": "GENERAL",
                    "is_active": True,
                    "vehicle_num": None,
                },
                {
                    "slot_id": 12,
                    "slot_name": "A002",
                    "category": "EV",
                    "is_active": False,
                    "vehicle_num": None,
                },
            ],
        )

    def test_should_attach_vehicle_num__when_projection_exists(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        repository = repository_module.ZoneSlotRepository(
            zone_client=self._build_zone_client(module=repository_module),
        )
        self.create_current_parking_view(
            vehicle_num="69가-3455",
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            slot_id=11,
            slot_name="A001",
            slot_type="GENERAL",
        )

        # When
        rows = repository.list_by_zone_id(zone_id=zone.zone_id)

        # Then
        self.assertEqual(rows[0]["vehicle_num"], "69가-3455")

    def test_should_pick_latest_vehicle_num__when_projection_duplicated(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        repository = repository_module.ZoneSlotRepository(
            zone_client=self._build_zone_client(module=repository_module),
        )
        now = timezone.now()
        self.create_current_parking_view(
            vehicle_num="11가-1111",
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            slot_id=11,
            slot_name="A001",
            slot_type="GENERAL",
            entry_at=now - timedelta(minutes=5),
        )
        self.create_current_parking_view(
            vehicle_num="22가-2222",
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            slot_id=11,
            slot_name="A001",
            slot_type="GENERAL",
            entry_at=now,
        )

        # When
        rows = repository.list_by_zone_id(zone_id=zone.zone_id)

        # Then
        self.assertEqual(rows[0]["vehicle_num"], "22가-2222")

    def test_should_order_slots__when_rows_loaded(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=13, slot_code="A003")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=12, slot_code="A002")
        repository = repository_module.ZoneSlotRepository(
            zone_client=self._build_zone_client(module=repository_module),
        )

        # When
        rows = repository.list_by_zone_id(zone_id=zone.zone_id)

        # Then
        self.assertEqual([row["slot_name"] for row in rows], ["A001", "A002", "A003"])

    def test_should_keep_empty_slots__when_projection_missing(self) -> None:
        # Given
        repository_module = self.load_repository_module()
        zone = self.create_zone(zone_name="A존")
        general = self.create_slot_type(type_name="GENERAL")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=11, slot_code="A001")
        self.create_zone_slot(zone=zone, slot_type=general, slot_id=12, slot_code="A002")
        repository = repository_module.ZoneSlotRepository(
            zone_client=self._build_zone_client(module=repository_module),
        )
        self.create_current_parking_view(
            vehicle_num="69가-3455",
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            slot_id=11,
            slot_name="A001",
            slot_type="GENERAL",
        )

        # When
        rows = repository.list_by_zone_id(zone_id=zone.zone_id)

        # Then
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["vehicle_num"], "69가-3455")
        self.assertIsNone(rows[1]["vehicle_num"])

    def _build_zone_client(self, *, module):
        return module.ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["GetZoneSlots"],
            )
        )
