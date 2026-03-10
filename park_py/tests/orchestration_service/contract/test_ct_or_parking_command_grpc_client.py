from __future__ import annotations

from datetime import datetime, timezone

from django.test import SimpleTestCase

from contracts.gen.python.parking_command.v1 import parking_command_pb2
from orchestration_service.clients.grpc.parking_command import ParkingCommandGrpcClient


class _FakeParkingCommandStub:
    def __init__(self) -> None:
        self.create_request = None
        self.compensate_request = None
        self.validate_request = None
        self.exit_request = None
        self.compensate_exit_request = None

    def CreateEntry(self, request, timeout=None):  # noqa: N802, ARG002
        self.create_request = request
        return parking_command_pb2.CreateEntryResponse(
            history_id=101,
            slot_id=request.slot_id,
            vehicle_num=request.vehicle_num,
            status="PARKED",
        )

    def CompensateEntry(self, request, timeout=None):  # noqa: N802, ARG002
        self.compensate_request = request
        return parking_command_pb2.CompensateEntryResponse(
            history_id=request.history_id,
            slot_released=True,
        )

    def ValidateActiveParking(self, request, timeout=None):  # noqa: N802, ARG002
        self.validate_request = request
        return type(
            "ValidateActiveParkingResponse",
            (),
            {
                "history_id": 101,
                "slot_id": 7,
                "vehicle_num": request.vehicle_num,
                "entry_at": parking_command_pb2.ValidateActiveParkingResponse().entry_at,
                "status": "PARKED",
                "zone_id": 1,
                "slot_type": "GENERAL",
            },
        )()

    def ExitParking(self, request, timeout=None):  # noqa: N802, ARG002
        self.exit_request = request
        return parking_command_pb2.ExitParkingResponse(
            history_id=101,
            slot_id=7,
            vehicle_num=request.vehicle_num,
            status="EXITED",
        )

    def CompensateExit(self, request, timeout=None):  # noqa: N802, ARG002
        self.compensate_exit_request = request
        return type(
            "CompensateExitResponse",
            (),
            {
                "history_id": request.history_id,
                "slot_occupied": True,
                "compensated_at": parking_command_pb2.CompensateExitResponse().compensated_at,
            },
        )()


class OrchestrationParkingCommandGrpcClientContractTests(SimpleTestCase):
    def test_should_build_create_entry_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PC-01] parking-command create-entry 계약 매핑"""

        # Given
        stub = _FakeParkingCommandStub()
        client = ParkingCommandGrpcClient(stub=stub)

        # When
        payload = client.create_entry(
            operation_id="entry-op-001",
            vehicle_num="12가3456",
            slot_id=7,
            requested_at="2026-03-10T10:00:00+09:00",
        )

        # Then
        self.assertEqual(stub.create_request.operation_id, "entry-op-001")
        self.assertEqual(stub.create_request.slot_id, 7)
        self.assertEqual(stub.create_request.vehicle_num, "12가3456")
        self.assertEqual(
            stub.create_request.context.requested_at.ToDatetime().isoformat(),
            datetime.fromisoformat("2026-03-10T10:00:00+09:00")
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
            .isoformat(),
        )
        self.assertEqual(payload["history_id"], 101)
        self.assertEqual(payload["status"], "PARKED")

    def test_should_build_compensate_entry_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PC-02] parking-command compensate-entry 계약 매핑"""

        # Given
        stub = _FakeParkingCommandStub()
        client = ParkingCommandGrpcClient(stub=stub)

        # When
        payload = client.compensate_entry(
            operation_id="entry-op-001",
            history_id=101,
            slot_id=7,
            vehicle_num="12가3456",
        )

        # Then
        self.assertEqual(stub.compensate_request.history_id, 101)
        self.assertEqual(stub.compensate_request.slot_id, 7)
        self.assertTrue(payload["slot_released"])

    def test_should_build_validate_active_parking_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PC-03] parking-command validate-active 계약 매핑"""

        # Given
        stub = _FakeParkingCommandStub()
        client = ParkingCommandGrpcClient(stub=stub)

        # When
        payload = client.validate_active_parking(vehicle_num="12가3456")

        # Then
        self.assertEqual(stub.validate_request.vehicle_num, "12가3456")
        self.assertEqual(payload["zone_id"], 1)
        self.assertEqual(payload["slot_type"], "GENERAL")

    def test_should_build_exit_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PC-04] parking-command exit 계약 매핑"""

        # Given
        stub = _FakeParkingCommandStub()
        client = ParkingCommandGrpcClient(stub=stub)

        # When
        payload = client.exit_parking(
            operation_id="exit-op-001",
            vehicle_num="12가3456",
            requested_at="2026-03-10T12:00:00+09:00",
        )

        # Then
        self.assertEqual(stub.exit_request.operation_id, "exit-op-001")
        self.assertEqual(payload["status"], "EXITED")

    def test_should_build_compensate_exit_request_and_map_response__when_called(self) -> None:
        """[CT-OR-GRPC-PC-05] parking-command compensate-exit 계약 매핑"""

        # Given
        stub = _FakeParkingCommandStub()
        client = ParkingCommandGrpcClient(stub=stub)

        # When
        payload = client.compensate_exit(
            operation_id="exit-op-001",
            history_id=101,
            slot_id=7,
            vehicle_num="12가3456",
        )

        # Then
        self.assertEqual(stub.compensate_exit_request.history_id, 101)
        self.assertTrue(payload["slot_occupied"])
