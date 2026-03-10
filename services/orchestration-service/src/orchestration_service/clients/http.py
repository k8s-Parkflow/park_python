from __future__ import annotations

import json
import socket
from time import sleep as default_sleep
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

from park_py.error_handling import ApplicationError, ErrorCode
from orchestration_service.policies.retry import RetryPolicy
from orchestration_service.policies.timeout import TimeoutPolicy


class DownstreamHttpError(Exception):
    def __init__(self, *, dependency: str, status_code: int, payload: dict) -> None:
        super().__init__(dependency)
        self.dependency = dependency
        self.status_code = status_code
        self.payload = payload


class JsonHttpClient:
    def __init__(
        self,
        *,
        timeout_seconds: float = 0.3,
        max_attempts: int = 3,
        backoff_seconds: tuple[float, ...] = (0.1, 0.2, 0.4),
        sleep=default_sleep,
        sender=None,
    ) -> None:
        self.timeout_policy = TimeoutPolicy(timeout_seconds=timeout_seconds)
        self.retry_policy = RetryPolicy(max_attempts=max_attempts)
        self.backoff_seconds = backoff_seconds
        self.sleep = sleep
        self.sender = sender or self._send_request

    def get(self, *, dependency: str, url: str) -> dict:
        request = Request(url, method="GET")
        return self._send(request=request, dependency=dependency)

    def post(self, *, dependency: str, url: str, payload: dict) -> dict:
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._send(request=request, dependency=dependency)

    def _send(self, *, request: Request, dependency: str) -> dict:
        attempt = 1
        while True:
            try:
                return self.sender(request=request, timeout=self.timeout_policy.timeout_seconds)
            except HTTPError as exc:
                raise DownstreamHttpError(
                    dependency=dependency,
                    status_code=exc.code,
                    payload=json.loads(exc.read().decode("utf-8")),
                ) from exc
            except (socket.timeout, TimeoutError, URLError) as exc:
                if self.retry_policy.should_retry(error_code="dependency_timeout", attempt=attempt):
                    self.sleep(self._backoff_for(attempt))
                    attempt += 1
                    continue

                raise ApplicationError(
                    code=ErrorCode.APPLICATION_ERROR,
                    status=503,
                    details={"dependency": dependency, "error_code": "dependency_timeout"},
                ) from exc

    def _backoff_for(self, attempt: int) -> float:
        index = min(attempt - 1, len(self.backoff_seconds) - 1)
        return self.backoff_seconds[index]

    def _send_request(self, *, request: Request, timeout: float) -> dict:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
