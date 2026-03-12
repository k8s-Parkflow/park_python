from __future__ import annotations

import io
import socket
import sys
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import Mock

from django.test import SimpleTestCase


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationHttpResilienceTests(SimpleTestCase):
    def test_should_retry_with_exponential_backoff__when_timeout_error_is_retryable(self) -> None:
        """[UT-OR-HTTP-01] retry/timeout 실행 경로"""

        from orchestration_service.saga.infrastructure.clients.http import JsonHttpClient

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
        from orchestration_service.saga.infrastructure.clients.http import JsonHttpClient

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

    def test_should_reject_non_http_scheme__when_dependency_url_is_invalid(self) -> None:
        """[UT-OR-HTTP-03] 허용되지 않은 URL scheme"""

        from park_py.error_handling import ApplicationError
        from orchestration_service.saga.infrastructure.clients.http import JsonHttpClient

        client = JsonHttpClient(sender=Mock())

        with self.assertRaises(ApplicationError) as context:
            client.get(dependency="vehicle-service", url="file:///tmp/vehicle.json")

        self.assertEqual(context.exception.status, 400)
        self.assertEqual(
            context.exception.details,
            {
                "error_code": "invalid_dependency_url_scheme",
                "scheme": "file",
            },
        )

    def test_should_wrap_non_json_http_error_body__when_downstream_returns_html(self) -> None:
        """[UT-OR-HTTP-04] 비 JSON HTTP 오류 본문 fallback"""

        from orchestration_service.saga.infrastructure.clients.http import (
            DownstreamHttpError,
            JsonHttpClient,
        )

        def sender(*, request, timeout):
            raise HTTPError(
                url=request.full_url,
                code=502,
                msg="Bad Gateway",
                hdrs=None,
                fp=io.BytesIO(b"<html>bad gateway</html>"),
            )

        client = JsonHttpClient(sender=sender)

        with self.assertRaises(DownstreamHttpError) as context:
            client.get(dependency="parking-query-service", url="http://service/internal/parking-query")

        self.assertEqual(context.exception.status_code, 502)
        self.assertEqual(
            context.exception.payload,
            {
                "error": {
                    "code": "invalid_downstream_error_response",
                    "message": "다운스트림 서비스가 JSON 오류 응답을 반환하지 않았습니다.",
                    "details": {"body": "<html>bad gateway</html>"},
                }
            },
        )
