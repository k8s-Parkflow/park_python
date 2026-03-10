from __future__ import annotations

from typing import Callable, TypeVar

import grpc

from park_py.error_handling.error_codes import ErrorCode
from park_py.error_handling.exceptions import ApplicationError


StubT = TypeVar("StubT")


class GrpcClientBase:
    def __init__(
        self,
        *,
        target: str | None = None,
        timeout: float = 5.0,
        channel: grpc.Channel | None = None,
        stub=None,
    ) -> None:
        self.target = target
        self.timeout = timeout
        self._channel = channel
        self._stub = stub

    def get_stub(self, stub_factory: Callable[[grpc.Channel], StubT]) -> StubT:
        if self._stub is not None:
            return self._stub
        if self._channel is None:
            self._channel = grpc.insecure_channel(self.target or "")
        self._stub = stub_factory(self._channel)
        return self._stub

    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()


class DownstreamDependencyError(ApplicationError):
    def __init__(self, *, message: str) -> None:
        super().__init__(
            message,
            code=ErrorCode.APPLICATION_ERROR,
            status=503,
        )

