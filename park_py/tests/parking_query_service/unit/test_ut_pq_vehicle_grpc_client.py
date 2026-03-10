from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from park_py.error_handling.exceptions import ApplicationError


class _UnavailableVehicleStub:
    def GetVehicle(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(code=grpc.StatusCode.UNAVAILABLE, details="vehicle service unavailable")


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class ParkingQueryVehicleGrpcClientUnitTests(SimpleTestCase):
    def test_should_raise_application_error__when_vehicle_service_unavailable(self) -> None:
        """[UT-PQ-VEHICLE-GRPC-01] vehicle gRPC 장애 전파"""

        from parking_query_service.clients.grpc.vehicle import VehicleGrpcClient

        client = VehicleGrpcClient(stub=_UnavailableVehicleStub())

        with self.assertRaises(ApplicationError) as context:
            client.exists_by_vehicle_num("12가3456")

        self.assertEqual(context.exception.status, 503)
