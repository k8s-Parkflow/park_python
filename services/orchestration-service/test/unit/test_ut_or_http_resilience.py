from __future__ import annotations

import socket
import sys
from pathlib import Path
from unittest.mock import Mock

from django.test import SimpleTestCase


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationHttpResilienceTests(SimpleTestCase):
    def test_should_retry_with_exponential_backoff__when_timeout_error_is_retryable(self) -> None:
        """[UT-OR-HTTP-01] retry/timeout 실행 경로"""

        from orchestration_service.clients.http import JsonHttpClient

        responses = [socket.timeout("timeout"), socket.timeout("timeout"), {"ok": True}]
        sleep_recorder = Mock()

        def sender(*, request, timeout):
            result = responses.pop(0)
            if isinstance(result, BaseException):
                raise result
            return result

        # Given
        client = JsonHttpClient(
            timeout_seconds=0.2,
            max_attempts=3,
            backoff_seconds=(0.1, 0.2, 0.4),
            sleep=sleep_recorder,
            sender=sender,
        )

        # When
        result = client.get(dependency="vehicle-service", url="http://service/internal/vehicles/12")

        # Then
        self.assertEqual(result, {"ok": True})
        self.assertEqual(sleep_recorder.call_args_list[0].args[0], 0.1)
        self.assertEqual(sleep_recorder.call_args_list[1].args[0], 0.2)

    def test_should_fail_after_retry_budget_is_exhausted__when_timeout_persists(self) -> None:
        """[UT-OR-HTTP-02] retry budget 소진"""

        from park_py.error_handling import ApplicationError
        from orchestration_service.clients.http import JsonHttpClient

        sleep_recorder = Mock()

        def sender(*, request, timeout):
            raise socket.timeout("timeout")

        # Given
        client = JsonHttpClient(
            timeout_seconds=0.2,
            max_attempts=2,
            backoff_seconds=(0.1, 0.2),
            sleep=sleep_recorder,
            sender=sender,
        )

        # When / Then
        with self.assertRaises(ApplicationError) as context:
            client.get(dependency="vehicle-service", url="http://service/internal/vehicles/12")

        self.assertEqual(context.exception.status, 503)
        self.assertEqual(sleep_recorder.call_count, 1)
