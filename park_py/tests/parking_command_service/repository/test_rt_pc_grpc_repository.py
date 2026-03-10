from __future__ import annotations

from django.test import TestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.domain import ParkingHistory, ParkingSlot
from parking_command_service.domains.parking_record.infrastructure.repositories.parking_record_repository import (
    DjangoParkingRecordRepository,
)


class ParkingCommandGrpcRepositoryTests(TestCase):
    def test_should_return_slot_by_identity_for_update__when_zone_metadata_matches(self) -> None:
        """[RT-PC-GRPC-03] zone metadata 기반 slot identity 조회"""

        slot = ParkingSlot.objects.create(
            slot_id=9,
            zone_id=2,
            slot_type_id=1,
            slot_code="C101",
            is_active=True,
        )

        loaded = DjangoParkingRecordRepository().get_slot_by_identity_for_update(
            zone_id=2,
            slot_code="C101",
        )

        self.assertEqual(loaded.slot_id, slot.slot_id)
        self.assertEqual(loaded.zone_id, 2)

    def test_should_return_history_for_update_with_slot__when_history_exists(self) -> None:
        """[RT-PC-GRPC-01] compensation용 이력 조회"""

        # Given
        slot = ParkingSlot.objects.create(
            slot_id=7,
            zone_id=1,
            slot_type_id=1,
            slot_code="A001",
            is_active=True,
        )
        history = ParkingHistory.objects.create(
            slot=slot,
            vehicle_num="12가3456",
            entry_at=timezone.now(),
        )

        # When
        loaded = DjangoParkingRecordRepository().get_history_for_update(history_id=history.history_id)

        # Then
        self.assertEqual(loaded.history_id, history.history_id)
        self.assertEqual(loaded.slot.slot_code, "A001")

    def test_should_return_active_history_with_slot__when_vehicle_has_active_session(self) -> None:
        """[RT-PC-GRPC-02] active-history 조회"""

        # Given
        slot = ParkingSlot.objects.create(
            slot_id=8,
            zone_id=1,
            slot_type_id=1,
            slot_code="A002",
            is_active=True,
        )
        ParkingHistory.objects.create(
            slot=slot,
            vehicle_num="34나5678",
            entry_at=timezone.now(),
        )

        # When
        loaded = DjangoParkingRecordRepository().get_active_history_for_vehicle(
            vehicle_num="34나5678"
        )

        # Then
        self.assertEqual(loaded.vehicle_num, "34나5678")
        self.assertEqual(loaded.slot.slot_code, "A002")
