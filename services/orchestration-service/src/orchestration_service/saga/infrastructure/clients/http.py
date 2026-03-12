from __future__ import annotations

import json
import socket
from time import sleep as default_sleep
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request
from urllib.request import urlopen

from orchestration_service.saga.domain.policies.retry import RetryPolicy
from orchestration_service.saga.domain.policies.timeout import TimeoutPolicy
from park_py.error_handling import ApplicationError, ErrorCode


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
        self._validate_url(url=url)
        request = Request(url, method="GET")
        return self._send(request=request, dependency=dependency)

    def post(self, *, dependency: str, url: str, payload: dict) -> dict:
        self._validate_url(url=url)
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
                    payload=self._decode_http_error_body(exc=exc),
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

    def _validate_url(self, *, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme in {"http", "https"}:
            return

        raise ApplicationError(
            code=ErrorCode.BAD_REQUEST,
            status=400,
            details={"error_code": "invalid_dependency_url_scheme", "scheme": parsed.scheme},
        )

    def _decode_http_error_body(self, *, exc: HTTPError) -> dict:
        raw_body = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {
                "error": {
                    "code": "invalid_downstream_error_response",
                    "message": "다운스트림 서비스가 JSON 오류 응답을 반환하지 않았습니다.",
                    "details": {"body": raw_body[:200]},
                }
            }

    def _send_request(self, *, request: Request, timeout: float) -> dict:
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw_body)
            except json.JSONDecodeError as exc:
                raise ApplicationError(
                    code=ErrorCode.APPLICATION_ERROR,
                    status=502,
                    details={
                        "error_code": "invalid_downstream_response",
                        "body": raw_body[:200],
                    },
                ) from exc
