from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

from park_py.error_handling import ApplicationError, ErrorCode


class DownstreamHttpError(Exception):
    def __init__(self, *, dependency: str, status_code: int, payload: dict) -> None:
        super().__init__(dependency)
        self.dependency = dependency
        self.status_code = status_code
        self.payload = payload


class JsonHttpClient:
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
        try:
            with urlopen(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise DownstreamHttpError(
                dependency=dependency,
                status_code=exc.code,
                payload=json.loads(exc.read().decode("utf-8")),
            ) from exc
        except URLError as exc:
            raise ApplicationError(
                code=ErrorCode.APPLICATION_ERROR,
                status=503,
                details={"dependency": dependency},
            ) from exc
