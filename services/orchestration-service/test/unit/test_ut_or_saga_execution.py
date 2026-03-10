import sys
from pathlib import Path
from unittest.mock import Mock

from django.test import SimpleTestCase

from park_py.error_handling import ApplicationError, ErrorCode


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationSagaExecutionUnitTests(SimpleTestCase):
    def test_should_mark_failed__when_entry_command_retry_is_exhausted(self) -> None:
        """[UT-OR-EXEC-01] 입차 command 재시도 소진 시 실패 기록"""

        from orchestration_service.application.entry_saga import EntrySagaOrchestrationService

        service = EntrySagaOrchestrationService(base_url="http://testserver")
        service.vehicle_client = Mock()
        service.zone_client = Mock()
        service.parking_command_client = Mock()
        service.parking_query_client = Mock()
        service.operation_repository = Mock()

        service.operation_repository.find_by_idempotency_key.return_value = None
        service.zone_client.get_entry_policy.return_value = {
            "entry_allowed": True,
            "zone_id": 1,
            "slot_type": "GENERAL",
        }
        service.parking_command_client.create_entry.side_effect = [
            ApplicationError(code=ErrorCode.APPLICATION_ERROR, status=503, details={"dependency": "parking-command-service"}),
            ApplicationError(code=ErrorCode.APPLICATION_ERROR, status=503, details={"dependency": "parking-command-service"}),
        ]

        with self.assertRaises(ApplicationError):
            service.execute(
                vehicle_num="12가3456",
                slot_id=7,
                requested_at="2026-03-10T10:00:00+09:00",
                idempotency_key="entry-failure-001",
            )

        service.operation_repository.mark_failed.assert_called_once()
        self.assertEqual(service.operation_repository.mark_failed.call_args.kwargs["failed_step"], "PARKING_COMMAND_ENTRY")
        service.operation_repository.mark_in_progress.assert_not_called()

    def test_should_mark_failed__when_exit_command_step_fails(self) -> None:
        """[UT-OR-EXEC-02] 출차 command 실패 기록"""

        from orchestration_service.application.exit_saga import ExitSagaOrchestrationService

        service = ExitSagaOrchestrationService(base_url="http://testserver")
        service.parking_command_client = Mock()
        service.parking_query_client = Mock()
        service.operation_repository = Mock()

        service.operation_repository.find_by_idempotency_key.return_value = None
        service.parking_query_client.get_current_parking.return_value = {
            "vehicle_num": "12가3456",
            "slot_id": 7,
            "zone_id": 1,
            "slot_type": "GENERAL",
            "entry_at": "2026-03-10T10:00:00+09:00",
        }
        service.parking_command_client.create_exit.side_effect = ApplicationError(
            code=ErrorCode.APPLICATION_ERROR,
            status=503,
            details={"dependency": "parking-command-service"},
        )

        with self.assertRaises(ApplicationError):
            service.execute(
                vehicle_num="12가3456",
                requested_at="2026-03-10T12:00:00+09:00",
                idempotency_key="exit-failure-001",
            )

        service.operation_repository.mark_failed.assert_called_once()
        self.assertEqual(service.operation_repository.mark_failed.call_args.kwargs["failed_step"], "PARKING_COMMAND_EXIT")
        service.operation_repository.mark_in_progress.assert_not_called()
