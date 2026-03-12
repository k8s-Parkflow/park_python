from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from contracts.gen.python.zone.v1 import zone_pb2


class _FakeZoneStub:
    def __init__(self) -> None:
        self.zone_request = None
        self.zone_slots_request = None

    def GetZone(self, request, timeout=None):  # noqa: N802, ARG002
        self.zone_request = request
        return zone_pb2.GetZoneResponse(
            zone_id=request.zone_id,
            zone_name="A존",
            is_active=True,
        )

    def GetZoneSlots(self, request, timeout=None):  # noqa: N802, ARG002
        self.zone_slots_request = request
        return zone_pb2.GetZoneSlotsResponse(
            zone_id=request.zone_id,
            slots=[
                zone_pb2.ZoneSlot(
                    slot_id=11,
                    slot_code="A001",
                    slot_type="GENERAL",
                    is_active=True,
                ),
                zone_pb2.ZoneSlot(
                    slot_id=12,
                    slot_code="A002",
                    slot_type="EV",
                    is_active=False,
                ),
            ],
        )


class _NotFoundZoneStub:
    def GetZone(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(code=grpc.StatusCode.NOT_FOUND, details="zone not found")


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class ParkingQueryZoneGrpcClientContractTests(SimpleTestCase):
    def test_should_build_get_zone_request__when_zone_exists(self) -> None:
        from parking_query_service.clients.grpc.zone import ZoneGrpcClient

        stub = _FakeZoneStub()
        client = ZoneGrpcClient(stub=stub)

        exists = client.exists_by_zone_id(1)

        self.assertTrue(exists)
        self.assertEqual(stub.zone_request.zone_id, 1)

    def test_should_return_false__when_zone_service_returns_not_found(self) -> None:
        from parking_query_service.clients.grpc.zone import ZoneGrpcClient

        client = ZoneGrpcClient(stub=_NotFoundZoneStub())

        exists = client.exists_by_zone_id(999)

        self.assertFalse(exists)

    def test_should_build_get_zone_slots_request__when_slots_are_requested(self) -> None:
        from parking_query_service.clients.grpc.zone import ZoneGrpcClient

        stub = _FakeZoneStub()
        client = ZoneGrpcClient(stub=stub)

        payload = client.get_zone_slots(zone_id=1)

        self.assertEqual(stub.zone_slots_request.zone_id, 1)
        self.assertEqual(
            payload,
            [
                {
                    "slot_id": 11,
                    "slot_name": "A001",
                    "category": "GENERAL",
                    "is_active": True,
                },
                {
                    "slot_id": 12,
                    "slot_name": "A002",
                    "category": "EV",
                    "is_active": False,
                },
            ],
        )
