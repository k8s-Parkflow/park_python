from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from contracts.gen.python.vehicle.v1 import vehicle_pb2
from contracts.gen.python.zone.v1 import zone_pb2
from orchestration_service.clients.grpc.vehicle import VehicleGrpcClient
from orchestration_service.clients.grpc.zone import ZoneGrpcClient


class _FakeVehicleStub:
    def __init__(self) -> None:
        self.request = None

    def GetVehicle(self, request, timeout=None):  # noqa: N802
        self.request = request
        return vehicle_pb2.GetVehicleResponse(
            vehicle_num=request.vehicle_num,
            vehicle_type="GENERAL",
            active=True,
        )


class _FakeZoneStub:
    def __init__(self) -> None:
        self.request = None

    def ValidateEntryPolicy(self, request, timeout=None):  # noqa: N802
        self.request = request
        return zone_pb2.ValidateEntryPolicyResponse(
            slot_id=request.slot_id,
            zone_id=1,
            slot_type="GENERAL",
            zone_active=True,
            entry_allowed=True,
            zone_name="A-1",
            slot_code="A001",
        )


class OrchestrationGrpcClientContractTests(SimpleTestCase):
    def test_should_build_vehicle_request_and_map_response__when_get_vehicle_is_called(self) -> None:
        """[CT-OR-GRPC-VEHICLE-01] 차량 gRPC 계약 매핑"""

        # Given
        stub = _FakeVehicleStub()
        client = VehicleGrpcClient(stub=stub)

        # When
        payload = client.get_vehicle(vehicle_num="12가3456")

        # Then
        self.assertEqual(stub.request.vehicle_num, "12가3456")
        self.assertEqual(
            payload,
            {
                "vehicle_num": "12가3456",
                "vehicle_type": "GENERAL",
                "active": True,
            },
        )

    def test_should_build_zone_request_and_map_response__when_validate_entry_policy_is_called(self) -> None:
        """[CT-OR-GRPC-ZONE-01] 구역 gRPC 계약 매핑"""

        # Given
        stub = _FakeZoneStub()
        client = ZoneGrpcClient(stub=stub)

        # When
        payload = client.validate_entry_policy(slot_id=7, vehicle_type="GENERAL")

        # Then
        self.assertEqual(stub.request.slot_id, 7)
        self.assertEqual(stub.request.vehicle_type, "GENERAL")
        self.assertEqual(
            payload,
            {
                "slot_id": 7,
                "zone_id": 1,
                "slot_type": "GENERAL",
                "zone_active": True,
                "entry_allowed": True,
                "zone_name": "A-1",
                "slot_code": "A001",
            },
        )
