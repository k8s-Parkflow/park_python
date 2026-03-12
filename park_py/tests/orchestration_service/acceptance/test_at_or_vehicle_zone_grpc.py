from __future__ import annotations

from unittest.mock import patch

from django.test import TransactionTestCase, override_settings

from park_py.tests.grpc_support import build_direct_stub
from park_py.tests.orchestration_service.support import (
    FakeParkingCommandGateway,
    FakeParkingQueryGateway,
)
from orchestration_service.clients.grpc.zone import ZoneGrpcClient
from orchestration_service.clients.grpc.vehicle import VehicleGrpcClient
from vehicle_service.vehicle.interfaces.grpc.servicers import VehicleGrpcServicer
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from zone_service.zone_catalog.interfaces.grpc.servicers import ZoneGrpcServicer
from zone_service.models import ParkingSlot, SlotType, Zone


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationVehicleZoneGrpcAcceptanceTests(TransactionTestCase):
    databases = "__all__"

    def test_should_complete_entry_saga_via_vehicle_and_zone_grpc_clients__when_servicers_are_available(self) -> None:
        """[AT-OR-GRPC-ENTRY-01] gRPC 계약 경유 차량/구역 검증"""

        # Given
        Vehicle.objects.create(
            vehicle_num="12가3456",
            vehicle_type=VehicleType.General,
        )
        zone = Zone.objects.create(zone_name="A-1", is_active=True)
        slot_type = SlotType.objects.create(type_name="GENERAL")
        ParkingSlot.objects.create(
            slot_id=7,
            zone=zone,
            slot_type=slot_type,
            slot_code="A001",
            is_active=True,
        )
        vehicle_gateway = VehicleGrpcClient(
            stub=build_direct_stub(
                servicer=VehicleGrpcServicer(),
                method_names=["GetVehicle"],
            )
        )
        zone_gateway = ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["ValidateEntryPolicy", "GetZone"],
            )
        )
        parking_command_gateway = FakeParkingCommandGateway(call_log=[])
        parking_query_gateway = FakeParkingQueryGateway(call_log=[])

        with patch(
            "orchestration_service.saga.bootstrap.build_vehicle_gateway",
            return_value=vehicle_gateway,
        ), patch(
            "orchestration_service.saga.bootstrap.build_zone_gateway",
            return_value=zone_gateway,
        ), patch(
            "orchestration_service.saga.bootstrap.build_parking_command_gateway",
            return_value=parking_command_gateway,
        ), patch(
            "orchestration_service.saga.bootstrap.build_parking_query_gateway",
            return_value=parking_query_gateway,
        ):
            # When
            response = self.client.post(
                "/api/v1/parking/entries",
                data={
                    "vehicle_num": "12가3456",
                    "slot_id": 7,
                    "requested_at": "2026-03-10T10:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="entry-grpc-idempotency-key-001",
            )

        # Then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "COMPLETED")
        self.assertEqual(response.json()["vehicle_num"], "12가3456")
        self.assertEqual(response.json()["slot_id"], 7)
