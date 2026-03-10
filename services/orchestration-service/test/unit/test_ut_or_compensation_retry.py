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
        from orchestration_service.clients.http import DownstreamHttpError

        clock = FrozenClock(timezone.now())
        repository = Mock()
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
            compensations=[compensation_action],
        )

        # Then
        self.assertEqual(result["status"], "COMPENSATED")
        self.assertEqual(sleep_recorder.call_args_list[0].args[0], 0.1)
        repository.mark_compensation_retry.assert_called_once()
        repository.mark_compensated.assert_called_once()

    def test_should_cancel_saga__when_compensation_deadline_is_exceeded(self) -> None:
        """[UT-OR-COMP-02] 보상 취소 전환"""

        from orchestration_service.application.compensation import CompensationRunner
        from orchestration_service.clients.http import DownstreamHttpError

        clock = FrozenClock(timezone.now())
        repository = Mock()
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
            compensations=[compensation_action],
        )

        # Then
        self.assertEqual(result["status"], "CANCELLED")
        repository.mark_cancelled.assert_called_once()
