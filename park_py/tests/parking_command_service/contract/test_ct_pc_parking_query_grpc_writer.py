from __future__ import annotations

from django.test import SimpleTestCase

from contracts.gen.python.parking_query.v1 import parking_query_pb2


class _FakeParkingQueryStub:
    def __init__(self) -> None:
        self.entry_request = None
        self.exit_request = None

    def ApplyEntryProjection(self, request, timeout=None):  # noqa: N802, ARG002
        self.entry_request = request
        return parking_query_pb2.ApplyEntryProjectionResponse(projected=True)

    def ApplyExitProjection(self, request, timeout=None):  # noqa: N802, ARG002
        self.exit_request = request
        return parking_query_pb2.ApplyExitProjectionResponse(projected=True)


class ParkingCommandParkingQueryGrpcWriterContractTests(SimpleTestCase):
    def test_should_build_apply_entry_projection_request__when_entry_recorded(self) -> None:
        """[CT-PC-PQ-GRPC-01] entry projection 요청 계약"""

        from parking_command_service.clients.grpc.parking_query import (
            ParkingQueryGrpcProjectionWriter,
        )

        history = _history_stub()
        stub = _FakeParkingQueryStub()
        writer = ParkingQueryGrpcProjectionWriter(stub=stub)

        writer.record_entry(history=history)

        self.assertEqual(stub.entry_request.history_id, 101)
        self.assertEqual(stub.entry_request.slot_type, "GENERAL")
        self.assertEqual(stub.entry_request.slot_id, 7)
        self.assertEqual(stub.entry_request.slot_code, "A001")

    def test_should_build_apply_exit_projection_request__when_exit_recorded(self) -> None:
        """[CT-PC-PQ-GRPC-02] exit projection 요청 계약"""

        from parking_command_service.clients.grpc.parking_query import (
            ParkingQueryGrpcProjectionWriter,
        )

        history = _history_stub()
        stub = _FakeParkingQueryStub()
        writer = ParkingQueryGrpcProjectionWriter(stub=stub)

        writer.record_exit(history=history)

        self.assertEqual(stub.exit_request.history_id, 101)
        self.assertEqual(stub.exit_request.slot_type, "GENERAL")
        self.assertEqual(stub.exit_request.slot_id, 7)
        self.assertEqual(stub.exit_request.slot_code, "A001")


def _history_stub():
    class _Slot:
        zone_id = 1
        slot_type_id = 1
        slot_code = "A001"

    class _History:
        history_id = 101
        vehicle_num = "12가3456"
        slot_id = 7
        slot = _Slot()
        entry_at = _AwareDateTime("2026-03-10T10:00:00+09:00")
        exit_at = _AwareDateTime("2026-03-10T12:00:00+09:00")

    return _History()


class _AwareDateTime:
    def __init__(self, isoformat_value: str) -> None:
        self._isoformat_value = isoformat_value

    def isoformat(self) -> str:
        return self._isoformat_value
