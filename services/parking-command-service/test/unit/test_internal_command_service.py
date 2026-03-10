import sys
from pathlib import Path

from unittest.mock import Mock, patch

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from park_py.error_handling import ApplicationError
from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingHistoryStatus
from parking_command_service.services import cancel_entry
from parking_command_service.services import _claim_operation_record

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from test.support.factories import create_slot
from test.support.factories import create_occupied_session


class InternalParkingCommandServiceUnitTests(TestCase):
    def test_should_reuse_cached_response__when_operation_claim_conflicts(self) -> None:
        """[UT-PC-INT-01] operation 선점 충돌 시 기존 응답 재사용"""

        existing_record = Mock(response_payload={"history_id": 101})

        with patch("parking_command_service.services.ParkingCommandOperation.objects") as manager:
            manager.create.side_effect = IntegrityError()
            manager.select_for_update.return_value.get.return_value = existing_record

            record, cached_response = _claim_operation_record(
                operation_id="entry-op-001",
                action="CREATE_ENTRY",
            )

        self.assertIs(record, existing_record)
        self.assertEqual(cached_response, {"history_id": 101})

    def test_should_fail_fast__when_claimed_operation_is_still_in_progress(self) -> None:
        """[UT-PC-INT-02] 미완료 operation row 재진입 차단"""

        existing_record = Mock(response_payload=None)

        with patch("parking_command_service.services.ParkingCommandOperation.objects") as manager:
            manager.create.side_effect = IntegrityError()
            manager.select_for_update.return_value.get.return_value = existing_record

            with self.assertRaises(ApplicationError) as context:
                _claim_operation_record(
                    operation_id="entry-op-002",
                    action="CREATE_ENTRY",
                )

        self.assertEqual(context.exception.status, 409)
        self.assertEqual(
            context.exception.details,
            {
                "error_code": "operation_in_progress",
                "operation_id": "entry-op-002",
                "action": "CREATE_ENTRY",
            },
        )

    def test_should_not_release_current_occupancy__when_cancelled_history_is_stale(self) -> None:
        """[UT-PC-INT-03] stale history 보상 시 현재 점유 유지"""

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
