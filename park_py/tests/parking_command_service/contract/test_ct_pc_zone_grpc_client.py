from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from contracts.gen.python.zone.v1 import zone_pb2


class _FakeZoneStub:
    def __init__(self) -> None:
        self.request = None

    def ValidateEntryPolicy(self, request, timeout=None):  # noqa: N802, ARG002
        self.request = request
        return zone_pb2.ValidateEntryPolicyResponse(
            slot_id=request.slot_id,
            zone_id=1,
            slot_type="GENERAL",
            zone_active=True,
            entry_allowed=True,
            zone_name="ZONE-1",
            slot_code="A001",
        )


class _UnavailableZoneStub:
    def ValidateEntryPolicy(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(code=grpc.StatusCode.UNAVAILABLE, details="zone unavailable")


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class ParkingCommandZoneGrpcClientContractTests(SimpleTestCase):
    def test_should_build_validate_entry_policy_request__when_called(self) -> None:
        """[CT-PC-ZONE-GRPC-01] zone validate-entry-policy 요청 계약"""

        from parking_command_service.clients.grpc.zone import ZoneGrpcClient

        stub = _FakeZoneStub()
        client = ZoneGrpcClient(stub=stub)

        payload = client.validate_entry_policy(slot_id=7, vehicle_type="GENERAL")

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
                "zone_name": "ZONE-1",
                "slot_code": "A001",
            },
        )
