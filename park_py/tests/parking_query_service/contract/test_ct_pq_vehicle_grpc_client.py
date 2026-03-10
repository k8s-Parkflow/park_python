from __future__ import annotations

import grpc
from django.test import SimpleTestCase

from contracts.gen.python.vehicle.v1 import vehicle_pb2


class _FakeVehicleStub:
    def __init__(self) -> None:
        self.request = None

    def GetVehicle(self, request, timeout=None):  # noqa: N802, ARG002
        self.request = request
        return vehicle_pb2.GetVehicleResponse(
            vehicle_num=request.vehicle_num,
            vehicle_type="GENERAL",
            active=True,
        )


class _NotFoundVehicleStub:
    def GetVehicle(self, request, timeout=None):  # noqa: N802, ARG002
        raise _FakeRpcError(code=grpc.StatusCode.NOT_FOUND, details="vehicle not found")


class _FakeRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class ParkingQueryVehicleGrpcClientContractTests(SimpleTestCase):
    def test_should_build_get_vehicle_request__when_vehicle_exists(self) -> None:
        """[CT-PQ-VEHICLE-GRPC-01] vehicle 조회 요청 계약"""

        from parking_query_service.clients.grpc.vehicle import VehicleGrpcClient

        stub = _FakeVehicleStub()
        client = VehicleGrpcClient(stub=stub)

        exists = client.exists_by_vehicle_num("12가3456")

        self.assertEqual(stub.request.vehicle_num, "12가3456")
        self.assertTrue(exists)

    def test_should_return_false__when_vehicle_service_returns_not_found(self) -> None:
        """[CT-PQ-VEHICLE-GRPC-02] vehicle 미존재 응답 계약"""

        from parking_query_service.clients.grpc.vehicle import VehicleGrpcClient

        client = VehicleGrpcClient(stub=_NotFoundVehicleStub())

        exists = client.exists_by_vehicle_num("99가9999")

        self.assertFalse(exists)
