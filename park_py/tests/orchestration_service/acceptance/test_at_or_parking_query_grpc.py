from __future__ import annotations

from unittest.mock import patch

from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from orchestration_service.clients.grpc.parking_command import ParkingCommandGrpcClient
from orchestration_service.clients.grpc.parking_query import ParkingQueryGrpcClient
from orchestration_service.clients.grpc.vehicle import VehicleGrpcClient
from orchestration_service.clients.grpc.zone import ZoneGrpcClient
from parking_command_service.clients.grpc.vehicle import VehicleGrpcClient as ParkingCommandVehicleGrpcClient
from parking_command_service.grpc.application import ParkingCommandGrpcApplicationService
from parking_command_service.grpc.servicers import ParkingCommandGrpcServicer
from parking_command_service.models import ParkingSlot, SlotOccupancy
from parking_query_service.grpc.servicers import ParkingQueryGrpcServicer
from parking_query_service.models import CurrentParkingView
from park_py.tests.grpc_support import build_direct_stub
from vehicle_service.vehicle.interfaces.grpc.servicers import VehicleGrpcServicer
from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from zone_service.zone_catalog.interfaces.grpc.servicers import ZoneGrpcServicer
from zone_service.models import ParkingSlot as ZoneParkingSlot
from zone_service.models import SlotType, Zone


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationParkingQueryGrpcAcceptanceTests(TransactionTestCase):
    def test_should_complete_entry_saga_with_real_parking_query_grpc__when_projection_is_applied(self) -> None:
        """[AT-OR-GRPC-PQ-01] 입차 SAGA가 parking-query gRPC projection까지 완료한다"""

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
        parking_command_gateway = ParkingCommandGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingCommandGrpcServicer(
                    application_service=ParkingCommandGrpcApplicationService(
                        vehicle_repository=ParkingCommandVehicleGrpcClient(
                            stub=build_direct_stub(
                                servicer=VehicleGrpcServicer(),
                                method_names=["GetVehicle"],
                            )
                        ),
                    )
                ),
                method_names=[
                    "CreateEntry",
                    "ValidateActiveParking",
                    "ExitParking",
                    "CompensateEntry",
                    "CompensateExit",
                ],
            )
        )
        parking_query_gateway = ParkingQueryGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingQueryGrpcServicer(),
                method_names=[
                    "ApplyEntryProjection",
                    "ApplyExitProjection",
                    "CompensateEntryProjection",
                    "CompensateExitProjection",
                    "GetCurrentParking",
                    "GetZoneAvailability",
                ],
            )
        )

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
                HTTP_IDEMPOTENCY_KEY="entry-grpc-idempotency-key-003",
            )

        # Then
        self.assertEqual(response.status_code, 201)
        projection = CurrentParkingView.objects.get(vehicle_num="12가3456")
        self.assertEqual(projection.slot_id, 7)
        self.assertEqual(projection.slot_code, "A001")
        self.assertEqual(projection.zone_id, zone.zone_id)
        self.assertEqual(projection.zone_name, "A-1")
        self.assertEqual(projection.slot_name, "A001")
        self.assertEqual(projection.slot_type, "GENERAL")

    def test_should_complete_exit_saga_with_real_parking_query_grpc__when_projection_is_removed(self) -> None:
        """[AT-OR-GRPC-PQ-02] 출차 SAGA가 parking-query gRPC projection 삭제까지 완료한다"""

        # Given
        slot = ParkingSlot.objects.create(
            slot_id=7,
            zone_id=1,
            slot_code="A001",
            is_active=True,
        )
        history = slot.parking_histories.create(
            vehicle_num="12가3456",
            entry_at=timezone.datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
        )
        CurrentParkingView.objects.create(
            vehicle_num="12가3456",
            history_id=history.history_id,
            zone_id=1,
            slot_id=7,
            slot_type="GENERAL",
            entry_at=history.entry_at,
        )

        SlotOccupancy.objects.create(
            slot=slot,
            occupied=True,
            vehicle_num="12가3456",
            history=history,
            occupied_at=history.entry_at,
        )

        parking_command_gateway = ParkingCommandGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingCommandGrpcServicer(
                    application_service=ParkingCommandGrpcApplicationService(
                        vehicle_repository=ParkingCommandVehicleGrpcClient(
                            stub=build_direct_stub(
                                servicer=VehicleGrpcServicer(),
                                method_names=["GetVehicle"],
                            )
                        ),
                    )
                ),
                method_names=["ValidateActiveParking", "ExitParking", "CompensateExit"],
            )
        )
        parking_query_gateway = ParkingQueryGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingQueryGrpcServicer(),
                method_names=[
                    "ApplyExitProjection",
                    "CompensateExitProjection",
                    "GetCurrentParking",
                ],
            )
        )

        with patch(
            "orchestration_service.dependencies.build_parking_command_gateway",
            return_value=parking_command_gateway,
        ), patch(
            "orchestration_service.dependencies.build_parking_query_gateway",
            return_value=parking_query_gateway,
        ):
            # When
            response = self.client.post(
                "/api/v1/parking/exits",
                data={
                    "vehicle_num": "12가3456",
                    "requested_at": "2026-03-10T12:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="exit-grpc-idempotency-key-002",
            )

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CurrentParkingView.objects.filter(vehicle_num="12가3456").exists())
