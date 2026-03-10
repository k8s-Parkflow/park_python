from __future__ import annotations

from unittest.mock import patch

from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from orchestration_service.clients.grpc.parking_command import ParkingCommandGrpcClient
from parking_command_service.grpc.servicers import ParkingCommandGrpcServicer
from parking_command_service.models import ParkingHistory, ParkingSlot, SlotOccupancy
from park_py.tests.grpc_support import build_direct_stub
from park_py.tests.orchestration_service.support import FakeParkingQueryGateway


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationParkingCommandGrpcExitAcceptanceTests(TransactionTestCase):
    def test_should_complete_exit_saga_via_parking_command_grpc__when_exit_servicer_is_available(self) -> None:
        """[AT-OR-GRPC-PC-EXIT-01] 출차 SAGA가 parking-command gRPC를 통해 완료된다"""

        # Given
        slot = ParkingSlot.objects.create(
            slot_id=7,
            zone_id=1,
            slot_type_id=1,
            slot_code="A001",
            is_active=True,
        )
        history = ParkingHistory.objects.create(
            slot=slot,
            zone_id=slot.zone_id,
            slot_type_id=slot.slot_type_id,
            slot_code=slot.slot_code,
            vehicle_num="12가3456",
            entry_at=timezone.datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
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
                servicer=ParkingCommandGrpcServicer(),
                method_names=["ValidateActiveParking", "ExitParking", "CompensateExit"],
            )
        )
        parking_query_gateway = FakeParkingQueryGateway(call_log=[])

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
                HTTP_IDEMPOTENCY_KEY="exit-grpc-idempotency-key-001",
            )

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "COMPLETED")
        self.assertEqual(ParkingHistory.objects.get(history_id=history.history_id).status, "EXITED")
        self.assertFalse(SlotOccupancy.objects.get(slot_id=7).occupied)

    def test_should_preserve_history_slot_metadata__when_slot_master_changes_after_entry(self) -> None:
        """[AT-OR-GRPC-PC-EXIT-02] active parking/exit는 history metadata를 우선한다"""

        slot = ParkingSlot.objects.create(
            slot_id=7,
            zone_id=1,
            slot_type_id=1,
            slot_code="A001",
            is_active=True,
        )
        history = ParkingHistory.objects.create(
            slot=slot,
            zone_id=slot.zone_id,
            slot_type_id=slot.slot_type_id,
            slot_code=slot.slot_code,
            vehicle_num="12가3456",
            entry_at=timezone.datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
        )
        SlotOccupancy.objects.create(
            slot=slot,
            occupied=True,
            vehicle_num="12가3456",
            history=history,
            occupied_at=history.entry_at,
        )
        slot.zone_id = 9
        slot.slot_type_id = 2
        slot.slot_code = "B999"
        slot.save(update_fields=["zone_id", "slot_type_id", "slot_code"])

        parking_command_gateway = ParkingCommandGrpcClient(
            stub=build_direct_stub(
                servicer=ParkingCommandGrpcServicer(),
                method_names=["ValidateActiveParking", "ExitParking"],
            )
        )

        active_parking = parking_command_gateway.validate_active_parking(vehicle_num="12가3456")
        exit_payload = parking_command_gateway.exit_parking(
            operation_id="exit-op-002",
            vehicle_num="12가3456",
            requested_at="2026-03-10T12:00:00+09:00",
        )

        self.assertEqual(active_parking["zone_id"], 1)
        self.assertEqual(active_parking["slot_type"], "GENERAL")
        self.assertEqual(active_parking["slot_code"], "A001")
        self.assertEqual(exit_payload["slot_code"], "A001")
