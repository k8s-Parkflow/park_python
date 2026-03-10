from __future__ import annotations

from django.test import SimpleTestCase

from contracts.gen.python.parking_query.v1 import parking_query_pb2
from orchestration_service.clients.grpc.parking_query import ParkingQueryGrpcClient


class _FakeParkingQueryStub:
    def __init__(self) -> None:
        self.apply_entry_request = None
        self.apply_exit_request = None
        self.compensate_entry_request = None
        self.compensate_exit_request = None
        self.current_request = None

    def ApplyEntryProjection(self, request, timeout=None):  # noqa: N802, ARG002
        self.apply_entry_request = request
        return parking_query_pb2.ApplyEntryProjectionResponse(projected=True)

    def ApplyExitProjection(self, request, timeout=None):  # noqa: N802, ARG002
        self.apply_exit_request = request
        return parking_query_pb2.ApplyExitProjectionResponse(projected=True)

    def CompensateEntryProjection(self, request, timeout=None):  # noqa: N802, ARG002
        self.compensate_entry_request = request
        return parking_query_pb2.CompensateEntryProjectionResponse(compensated=True)

    def CompensateExitProjection(self, request, timeout=None):  # noqa: N802, ARG002
        self.compensate_exit_request = request
        return parking_query_pb2.CompensateExitProjectionResponse(compensated=True)

    def GetCurrentParking(self, request, timeout=None):  # noqa: N802, ARG002
        self.current_request = request
        return parking_query_pb2.GetCurrentParkingResponse(
            vehicle_num=request.vehicle_num,
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
        )


class OrchestrationParkingQueryGrpcClientContractTests(SimpleTestCase):
    def test_should_build_apply_entry_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PQ-01] parking-query apply-entry 계약 매핑"""

        stub = _FakeParkingQueryStub()
        client = ParkingQueryGrpcClient(stub=stub)

        payload = client.apply_entry_projection(
            operation_id="entry-op-001",
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            entry_at="2026-03-10T10:00:00+09:00",
        )

        self.assertEqual(stub.apply_entry_request.history_id, 101)
        self.assertTrue(payload["projected"])

    def test_should_build_apply_exit_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PQ-02] parking-query apply-exit 계약 매핑"""

        stub = _FakeParkingQueryStub()
        client = ParkingQueryGrpcClient(stub=stub)

        payload = client.apply_exit_projection(
            operation_id="exit-op-001",
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            exit_at="2026-03-10T12:00:00+09:00",
        )

        self.assertEqual(stub.apply_exit_request.history_id, 101)
        self.assertTrue(payload["projected"])

    def test_should_build_compensation_requests__when_called(self) -> None:
        """[CT-OR-GRPC-PQ-03] parking-query compensation 계약 매핑"""

        stub = _FakeParkingQueryStub()
        client = ParkingQueryGrpcClient(stub=stub)

        entry_payload = client.compensate_entry_projection(
            operation_id="entry-op-001",
            history_id=101,
            vehicle_num="12가3456",
            zone_id=1,
            slot_type="GENERAL",
        )
        exit_payload = client.compensate_exit_projection(
            operation_id="exit-op-001",
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            entry_at="2026-03-10T10:00:00+09:00",
        )

        self.assertEqual(stub.compensate_entry_request.zone_id, 1)
        self.assertEqual(stub.compensate_exit_request.slot_id, 7)
        self.assertTrue(entry_payload["compensated"])
        self.assertTrue(exit_payload["compensated"])

    def test_should_build_get_current_parking_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PQ-04] parking-query current-parking 계약 매핑"""

        stub = _FakeParkingQueryStub()
        client = ParkingQueryGrpcClient(stub=stub)

        payload = client.get_current_parking(vehicle_num="12가3456")

        self.assertEqual(stub.current_request.vehicle_num, "12가3456")
        self.assertEqual(payload["slot_id"], 7)
