from __future__ import annotations

import sys
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

from django.test import SimpleTestCase
from django.utils import timezone


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class FrozenClock:
    def __init__(self, start: datetime) -> None:
        self.current = start

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += timedelta(seconds=seconds)


class OrchestrationCompensationRetryTests(SimpleTestCase):
    def test_should_retry_compensation_with_backoff__when_compensation_eventually_succeeds(self) -> None:
        """[UT-OR-COMP-01] 보상 지수 백오프 재시도"""

        from orchestration_service.application.compensation import CompensationRunner
        from orchestration_service.application.compensation import CompensationAction
        from orchestration_service.clients.http import DownstreamHttpError

        clock = FrozenClock(timezone.now())
        repository = Mock()
        repository.get.return_value.completed_compensations = []
        sleep_recorder = Mock(side_effect=lambda seconds: clock.advance(seconds))

        attempts = [
            DownstreamHttpError(
                dependency="parking-query-service",
                status_code=503,
                payload={"error": {"code": "dependency_timeout", "message": "timeout"}},
            ),
            {"restored": True},
        ]

        def compensation_action():
            result = attempts.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        runner = CompensationRunner(
            repository=repository,
            clock=clock.now,
            sleep=sleep_recorder,
            backoff_seconds=(0.1, 0.2, 0.4),
            ttl_seconds=1.0,
        )

        # When
        result = runner.run(
            operation_id="entry-op-001",
            failed_step="UPDATE_QUERY_ENTRY",
            compensations=[
                CompensationAction(step_key="REVERT_QUERY_ENTRY", run=compensation_action),
            ],
        )

        # Then
        self.assertEqual(result["status"], "COMPENSATED")
        self.assertEqual(sleep_recorder.call_args_list[0].args[0], 0.1)
        repository.mark_compensation_retry.assert_called_once()
        repository.mark_compensated.assert_called_once()

    def test_should_cancel_saga__when_compensation_deadline_is_exceeded(self) -> None:
        """[UT-OR-COMP-02] 보상 취소 전환"""

        from orchestration_service.application.compensation import CompensationRunner
        from orchestration_service.application.compensation import CompensationAction
        from orchestration_service.clients.http import DownstreamHttpError

        clock = FrozenClock(timezone.now())
        repository = Mock()
        repository.get.return_value.completed_compensations = []
        sleep_recorder = Mock(side_effect=lambda seconds: clock.advance(seconds))

        def compensation_action():
            raise DownstreamHttpError(
                dependency="parking-command-service",
                status_code=503,
                payload={"error": {"code": "dependency_timeout", "message": "timeout"}},
            )

        runner = CompensationRunner(
            repository=repository,
            clock=clock.now,
            sleep=sleep_recorder,
            backoff_seconds=(0.3, 0.6, 1.2),
            ttl_seconds=0.5,
        )

        # When
        result = runner.run(
            operation_id="entry-op-001",
            failed_step="UPDATE_QUERY_ENTRY",
            compensations=[
                CompensationAction(step_key="CANCEL_PARKING_ENTRY", run=compensation_action),
            ],
        )

        # Then
        self.assertEqual(result["status"], "CANCELLED")
        repository.mark_cancelled.assert_called_once()

    def test_should_resume_from_first_incomplete_compensation__when_retry_restarts(self) -> None:
        """[UT-OR-COMP-03] 완료된 보상 단계 skip"""

        from orchestration_service.application.compensation import CompensationAction
        from orchestration_service.application.compensation import CompensationRunner
        from orchestration_service.clients.http import DownstreamHttpError

        clock = FrozenClock(timezone.now())
        repository = Mock()
        repository.get.return_value.completed_compensations = ["RESTORE_QUERY_EXIT"]
        sleep_recorder = Mock(side_effect=lambda seconds: clock.advance(seconds))
        restore_query = Mock()

        attempts = [
            DownstreamHttpError(
                dependency="parking-command-service",
                status_code=503,
                payload={"error": {"code": "dependency_timeout", "message": "timeout"}},
            ),
            {"restored": True},
        ]

        def restore_command():
            result = attempts.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        runner = CompensationRunner(
            repository=repository,
            clock=clock.now,
            sleep=sleep_recorder,
            backoff_seconds=(0.1, 0.2, 0.4),
            ttl_seconds=1.0,
        )

        result = runner.run(
            operation_id="exit-op-001",
            failed_step="UPDATE_QUERY_EXIT",
            compensations=[
                CompensationAction(step_key="RESTORE_QUERY_EXIT", run=restore_query),
                CompensationAction(step_key="RESTORE_PARKING_EXIT", run=restore_command),
            ],
        )

        self.assertEqual(result["status"], "COMPENSATED")
        restore_query.assert_not_called()
        repository.mark_compensation_step_completed.assert_called_once_with(
            operation_id="exit-op-001",
            step_key="RESTORE_PARKING_EXIT",
        )
