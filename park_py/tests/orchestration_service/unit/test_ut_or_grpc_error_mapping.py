from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from orchestration_service.application.errors import DownstreamError
from orchestration_service.clients.grpc.base import map_rpc_error


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class OrchestrationGrpcErrorMappingUnitTests(SimpleTestCase):
    def test_should_raise_not_found_error__when_rpc_status_is_not_found(self) -> None:
        """[UT-OR-GRPC-01] NOT_FOUND 매핑"""

        # Given
        error = _FakeRpcError(code=grpc.StatusCode.NOT_FOUND, details="vehicle not found")

        # When
        mapped = map_rpc_error(dependency="vehicle-service", error=error)

        # Then
        self.assertIsInstance(mapped, DownstreamError)
        self.assertEqual(mapped.error_code, "not_found")
        self.assertEqual(mapped.status, 404)

    def test_should_raise_dependency_unavailable_error__when_rpc_status_is_unavailable(self) -> None:
        """[UT-OR-GRPC-02] UNAVAILABLE 매핑"""

        # Given
        error = _FakeRpcError(code=grpc.StatusCode.UNAVAILABLE, details="service unavailable")

        # When
        mapped = map_rpc_error(dependency="zone-service", error=error)

        # Then
        self.assertIsInstance(mapped, DownstreamError)
        self.assertEqual(mapped.error_code, "dependency_unavailable")
        self.assertEqual(mapped.status, 503)
