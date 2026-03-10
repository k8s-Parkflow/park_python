from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings

from orchestration_service.models import SagaOperation
from park_py.tests.orchestration_service.support import (
    FakeParkingCommandGateway,
    FakeParkingQueryGateway,
    FakeVehicleGateway,
    FakeZoneGateway,
    projection_error,
)


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationGatewayAcceptanceTests(TestCase):
    def test_should_complete_entry_saga_via_gateway__when_dependencies_succeed(self) -> None:
        """[AT-OR-ENTRY-01] 입차 성공"""

        call_log: list[str] = []
        vehicle_gateway = FakeVehicleGateway(call_log=call_log)
        zone_gateway = FakeZoneGateway(call_log=call_log)
        parking_command_gateway = FakeParkingCommandGateway(call_log=call_log)
        parking_query_gateway = FakeParkingQueryGateway(call_log=call_log)

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
            # Given
            payload = {
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "requested_at": "2026-03-10T10:00:00+09:00",
            }

            # When
            response = self.client.post(
                "/api/v1/parking/entries",
                data=payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-001",
            )

        # Then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "COMPLETED")
        self.assertEqual(
            call_log,
            [
                "vehicle-service",
                "zone-service",
                "parking-command-service",
                "parking-query-service",
            ],
        )

    def test_should_compensate_entry__when_projection_update_fails(self) -> None:
        """[AT-OR-ENTRY-02] 입차 중 projection 실패 시 보상"""

        call_log: list[str] = []
        vehicle_gateway = FakeVehicleGateway(call_log=call_log)
        zone_gateway = FakeZoneGateway(call_log=call_log)
        parking_command_gateway = FakeParkingCommandGateway(call_log=call_log)
        parking_query_gateway = FakeParkingQueryGateway(
            call_log=call_log,
            entry_error=projection_error(),
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
            # Given
            payload = {
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "requested_at": "2026-03-10T10:00:00+09:00",
            }

            # When
            response = self.client.post(
                "/api/v1/parking/entries",
                data=payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-002",
            )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            parking_query_gateway.compensations,
            ["COMPENSATE_QUERY_ENTRY"],
        )
        self.assertEqual(
            parking_command_gateway.compensations,
            ["COMPENSATE_PARKING_ENTRY"],
        )

    def test_should_reuse_existing_entry_result__when_same_idempotency_key_reenters(self) -> None:
        """[AT-OR-ENTRY-04] 입차 멱등 재요청"""

        call_log: list[str] = []
        vehicle_gateway = FakeVehicleGateway(call_log=call_log)
        zone_gateway = FakeZoneGateway(call_log=call_log)
        parking_command_gateway = FakeParkingCommandGateway(call_log=call_log)
        parking_query_gateway = FakeParkingQueryGateway(call_log=call_log)

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
            payload = {
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "requested_at": "2026-03-10T10:00:00+09:00",
            }

            first_response = self.client.post(
                "/api/v1/parking/entries",
                data=payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-003",
            )
            second_response = self.client.post(
                "/api/v1/parking/entries",
                data=payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-003",
            )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 201)
        self.assertEqual(first_response.json(), second_response.json())
        self.assertEqual(len(call_log), 4)

    def test_should_complete_exit_saga_via_gateway__when_dependencies_succeed(self) -> None:
        """[AT-OR-EXIT-01] 출차 성공"""

        call_log: list[str] = []
        parking_command_gateway = FakeParkingCommandGateway(call_log=call_log)
        parking_query_gateway = FakeParkingQueryGateway(call_log=call_log)

        with patch(
            "orchestration_service.dependencies.build_parking_command_gateway",
            return_value=parking_command_gateway,
        ), patch(
            "orchestration_service.dependencies.build_parking_query_gateway",
            return_value=parking_query_gateway,
        ):
            payload = {
                "vehicle_num": "12가3456",
                "requested_at": "2026-03-10T12:00:00+09:00",
            }

            response = self.client.post(
                "/api/v1/parking/exits",
                data=payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="exit-idempotency-key-001",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "COMPLETED")
        self.assertEqual(
            call_log,
            [
                "parking-command-service",
                "parking-command-service",
                "parking-query-service",
            ],
        )

    def test_should_return_saga_status__when_operation_is_requested(self) -> None:
        """[AT-OR-CORE-01] 사가 상태 조회"""

        operation = SagaOperation.objects.create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="FAILED",
            current_step="UPDATE_QUERY_ENTRY",
            idempotency_key="entry-idempotency-key-010",
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            last_error_code="projection_update_failed",
            last_error_message="parking-query-service timeout",
        )

        response = self.client.get(f"/api/v1/saga-operations/{operation.operation_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["operation_id"], "entry-op-001")
