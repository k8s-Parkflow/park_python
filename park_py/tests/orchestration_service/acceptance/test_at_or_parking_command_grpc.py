from __future__ import annotations

from unittest.mock import patch

from django.test import TransactionTestCase, override_settings

from orchestration_service.clients.grpc.parking_command import ParkingCommandGrpcClient
from orchestration_service.clients.grpc.vehicle import VehicleGrpcClient
from orchestration_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient as ParkingCommandVehicleGrpcClient
from parking_command_service.grpc.application import ParkingCommandGrpcApplicationService
from parking_command_service.models import ParkingHistory, ParkingSlot, SlotOccupancy
from parking_command_service.grpc.servicers import ParkingCommandGrpcServicer
from park_py.tests.grpc_support import build_direct_stub
from park_py.tests.orchestration_service.support import FakeParkingQueryGateway
from vehicle_service.grpc.servicers import VehicleGrpcServicer
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from zone_service.grpc.servicers import ZoneGrpcServicer
from zone_service.models import ParkingSlot as ZoneParkingSlot
from zone_service.models import SlotType, Zone


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationParkingCommandGrpcAcceptanceTests(TransactionTestCase):
    def test_should_complete_entry_saga_via_parking_command_grpc__when_servicer_is_available(self) -> None:
        """[AT-OR-GRPC-PC-01] 입차 SAGA가 parking-command gRPC를 통해 완료된다"""

        # Given
        Vehicle.objects.create(vehicle_num="12가3456", vehicle_type=VehicleType.General)
        zone = Zone.objects.create(zone_name="A-1", is_active=True)
        slot_type = SlotType.objects.create(type_name="GENERAL")
        ZoneParkingSlot.objects.create(
            slot_id=7,
            zone=zone,
            slot_type=slot_type,
            slot_code="A001",
            is_active=True,
        )
        ParkingSlot.objects.create(
            slot_id=7,
            zone_id=zone.zone_id,
            slot_type_id=1,
            slot_code="A001",
            is_active=True,
        )

        vehicle_gateway = VehicleGrpcClient(
            stub=build_direct_stub(servicer=VehicleGrpcServicer(), method_names=["GetVehicle"])
        )
        zone_gateway = ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["ValidateEntryPolicy", "GetZone"],
            )
        )
        parking_command_vehicle_lookup = ParkingCommandVehicleGrpcClient(
            stub=build_direct_stub(servicer=VehicleGrpcServicer(), method_names=["GetVehicle"])
        )
        parking_command_gateway = ParkingCommandGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingCommandGrpcServicer(
                    application_service=ParkingCommandGrpcApplicationService(
                        vehicle_repository=parking_command_vehicle_lookup,
                    )
                ),
                method_names=["CreateEntry", "CompensateEntry"],
            )
        )
        parking_query_gateway = FakeParkingQueryGateway(call_log=[])

        with patch(
            "orchestration_service.dependencies.build_vehicle_gateway",
            return_value=vehicle_gateway,
        ), patch(
            "orchestration_service.dependencies.build_zone_gateway",
            return_value=zone_gateway,
        ), patch(
            "orchestration_service.dependencies.build_parking_command_gateway",
            return_value=parking_command_gateway,
        ), patch(
            "orchestration_service.dependencies.build_parking_query_gateway",
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
                HTTP_IDEMPOTENCY_KEY="entry-grpc-idempotency-key-002",
            )

        # Then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ParkingHistory.objects.count(), 1)
        self.assertTrue(SlotOccupancy.objects.get(slot_id=7).occupied)

    def test_should_persist_zone_metadata_snapshot__when_command_slot_master_differs(self) -> None:
        """[AT-OR-GRPC-PC-02] trusted gRPC entry는 zone metadata snapshot을 우선한다"""

        # Given
        Vehicle.objects.create(vehicle_num="12가3456", vehicle_type=VehicleType.General)
        zone = Zone.objects.create(zone_name="A-1", is_active=True)
        slot_type = SlotType.objects.create(type_name="GENERAL")
        ZoneParkingSlot.objects.create(
            slot_id=7,
            zone=zone,
            slot_type=slot_type,
            slot_code="A001",
            is_active=True,
        )
        ParkingSlot.objects.create(
            slot_id=7,
            zone_id=999,
            slot_type_id=2,
            slot_code="B999",
            is_active=False,
        )

        vehicle_gateway = VehicleGrpcClient(
            stub=build_direct_stub(servicer=VehicleGrpcServicer(), method_names=["GetVehicle"])
        )
        zone_gateway = ZoneGrpcClient(
            stub=build_direct_stub(
                servicer=ZoneGrpcServicer(),
                method_names=["ValidateEntryPolicy", "GetZone"],
            )
        )
        parking_command_vehicle_lookup = ParkingCommandVehicleGrpcClient(
            stub=build_direct_stub(servicer=VehicleGrpcServicer(), method_names=["GetVehicle"])
        )
        parking_command_gateway = ParkingCommandGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingCommandGrpcServicer(
                    application_service=ParkingCommandGrpcApplicationService(
                        vehicle_repository=parking_command_vehicle_lookup,
                    )
                ),
                method_names=["CreateEntry", "CompensateEntry"],
            )
        )
        parking_query_gateway = FakeParkingQueryGateway(call_log=[])

        with patch(
            "orchestration_service.dependencies.build_vehicle_gateway",
            return_value=vehicle_gateway,
        ), patch(
            "orchestration_service.dependencies.build_zone_gateway",
            return_value=zone_gateway,
        ), patch(
            "orchestration_service.dependencies.build_parking_command_gateway",
            return_value=parking_command_gateway,
        ), patch(
            "orchestration_service.dependencies.build_parking_query_gateway",
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
                HTTP_IDEMPOTENCY_KEY="entry-grpc-idempotency-key-004",
            )

        # Then
        self.assertEqual(response.status_code, 201)
        history = ParkingHistory.objects.get()
        self.assertEqual(history.zone_id, zone.zone_id)
        self.assertEqual(history.slot_type_id, 1)
        self.assertEqual(history.slot_code, "A001")
        self.assertTrue(SlotOccupancy.objects.filter(slot_id=7, occupied=True).exists())
