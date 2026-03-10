from __future__ import annotations

from django.test import TestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.domain import ParkingHistory, ParkingSlot
from parking_command_service.domains.parking_record.infrastructure.repositories.parking_record_repository import (
    DjangoParkingRecordRepository,
)


class ParkingCommandGrpcRepositoryTests(TestCase):
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
