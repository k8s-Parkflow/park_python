from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, TypeVar

import grpc

from contracts.gen.python.common.v1 import common_pb2
from orchestration_service.saga.application.errors import DownstreamError


StubT = TypeVar("StubT")


def map_rpc_error(*, dependency: str, error: grpc.RpcError) -> DownstreamError:
    status_code = error.code()
    details = error.details() or "grpc dependency call failed"

    if status_code == grpc.StatusCode.NOT_FOUND:
        return DownstreamError(
            dependency=dependency,
            error_code="not_found",
            message=details,
            status=404,
        )
    if status_code == grpc.StatusCode.INVALID_ARGUMENT:
        return DownstreamError(
            dependency=dependency,
            error_code="validation_error",
            message=details,
            status=400,
        )
    if status_code in {grpc.StatusCode.ALREADY_EXISTS, grpc.StatusCode.FAILED_PRECONDITION}:
        return DownstreamError(
            dependency=dependency,
            error_code="conflict",
            message=details,
            status=409,
        )
    if status_code == grpc.StatusCode.UNAVAILABLE:
        return DownstreamError(
            dependency=dependency,
            error_code="dependency_unavailable",
            message=details,
            status=503,
        )
    if status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
        return DownstreamError(
            dependency=dependency,
            error_code="timeout",
            message=details,
            status=504,
        )
    return DownstreamError(
        dependency=dependency,
        error_code="dependency_error",
        message=details,
        status=502,
    )


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

    def invoke_unary(self, *, dependency: str, rpc_call, request):
        try:
            return rpc_call(request, timeout=self.timeout)
        except grpc.RpcError as error:
            raise map_rpc_error(dependency=dependency, error=error) from error

    def close(self) -> None:
        if self._channel is not None:
            self._channel.close()


def build_request_context(
    *,
    idempotency_key: str = "",
    requested_at: str | None = None,
) -> common_pb2.RequestContext:
    context = common_pb2.RequestContext(idempotency_key=idempotency_key)
    if requested_at:
        requested_datetime = datetime.fromisoformat(requested_at)
        if requested_datetime.tzinfo is None:
            requested_datetime = requested_datetime.replace(tzinfo=timezone.utc)
        context.requested_at.FromDatetime(requested_datetime.astimezone(timezone.utc))
    return context
