import sys
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingHistoryStatus
from parking_command_service.services import cancel_entry

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from test.support.factories import create_slot
from test.support.factories import create_occupied_session


class InternalParkingCommandServiceUnitTests(TestCase):
    def test_should_not_release_current_occupancy__when_cancelled_history_is_stale(self) -> None:
        """[UT-PC-INT-01] stale history 보상 시 현재 점유 유지"""

        slot = create_slot()
        stale_history = ParkingHistory.objects.create(
            slot=slot,
            vehicle_num="11가1111",
            status=ParkingHistoryStatus.EXITED,
            entry_at=timezone.now(),
            exit_at=timezone.now(),
        )
        current_history, occupancy = create_occupied_session(
            slot=slot,
            vehicle_num="22가2222",
            entry_at=timezone.now(),
        )

        response = cancel_entry(
            operation_id="cancel-entry-001",
            history_id=stale_history.history_id,
        )

        occupancy.refresh_from_db()
        self.assertEqual(response, {"history_id": stale_history.history_id, "slot_released": True})
        self.assertTrue(occupancy.occupied)
        self.assertEqual(occupancy.history_id, current_history.history_id)
        self.assertTrue(ParkingHistory.objects.filter(history_id=current_history.history_id).exists())
