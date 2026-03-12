from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from park_py.error_handling.exceptions import ApplicationError


class _UnavailableZoneStub:
    def GetZone(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(code=grpc.StatusCode.UNAVAILABLE, details="zone service unavailable")

    def GetZoneSlots(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(code=grpc.StatusCode.UNAVAILABLE, details="zone service unavailable")


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class ParkingQueryZoneGrpcClientUnitTests(SimpleTestCase):
    def test_should_raise_application_error__when_zone_lookup_fails(self) -> None:
        from parking_query_service.clients.grpc.zone import ZoneGrpcClient

        client = ZoneGrpcClient(stub=_UnavailableZoneStub())

        with self.assertRaises(ApplicationError) as context:
            client.exists_by_zone_id(1)

        self.assertEqual(context.exception.status, 503)

    def test_should_raise_application_error__when_zone_slots_lookup_fails(self) -> None:
        from parking_query_service.clients.grpc.zone import ZoneGrpcClient

        client = ZoneGrpcClient(stub=_UnavailableZoneStub())

        with self.assertRaises(ApplicationError) as context:
            client.get_zone_slots(zone_id=1)

        self.assertEqual(context.exception.status, 503)
