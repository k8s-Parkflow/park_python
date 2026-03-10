from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from park_py.error_handling.exceptions import ApplicationError


class _UnavailableParkingQueryStub:
    def ApplyEntryProjection(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(
            code=grpc.StatusCode.UNAVAILABLE,
            details="parking-query service unavailable",
        )


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class ParkingCommandParkingQueryGrpcWriterUnitTests(SimpleTestCase):
    def test_should_raise_application_error__when_projection_service_unavailable(self) -> None:
        """[UT-PC-PQ-GRPC-01] projection gRPC 장애 전파"""

        from parking_command_service.clients.grpc.parking_query import (
            ParkingQueryGrpcProjectionWriter,
        )

        writer = ParkingQueryGrpcProjectionWriter(stub=_UnavailableParkingQueryStub())

        with self.assertRaises(ApplicationError) as context:
            writer.record_entry(history=_history_stub())

        self.assertEqual(context.exception.status, 503)


def _history_stub():
    class _History:
        history_id = 101
        vehicle_num = "12가3456"
        slot_id = 7
        zone_id = 1
        slot_type_id = 1
        slot_code = "A001"
        entry_at = _AwareDateTime("2026-03-10T10:00:00+09:00")
        exit_at = _AwareDateTime("2026-03-10T12:00:00+09:00")

    return _History()


class _AwareDateTime:
    def __init__(self, isoformat_value: str) -> None:
        self._isoformat_value = isoformat_value

    def isoformat(self) -> str:
        return self._isoformat_value
