import sys
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationGatewayContractTests(SimpleTestCase):
    @patch("orchestration_service.views.EntrySagaOrchestrationService")
    def test_should_match_entry_gateway_response_schema__when_entry_request_succeeds(
        self,
        entry_saga_service_class,
    ) -> None:
        """[CT-OR-API-01] 입차 API 계약"""

        entry_saga_service_class.return_value.execute.return_value = {
            "operation_id": "entry-op-001",
            "status": "COMPLETED",
            "history_id": 101,
            "vehicle_num": "12가3456",
            "slot_id": 7,
            "entry_at": "2026-03-10T10:00:00+09:00",
        }

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
        self.assertEqual(
            response.json(),
            {
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "entry_at": "2026-03-10T10:00:00+09:00",
            },
        )

    @patch("orchestration_service.views.ExitSagaOrchestrationService")
    def test_should_match_exit_gateway_error_schema__when_exit_saga_is_compensated(
        self,
        exit_saga_service_class,
    ) -> None:
        """[CT-OR-API-02] 출차 API 계약"""

        exit_saga_service_class.return_value.execute.return_value = {
            "operation_id": "exit-op-001",
            "status": "COMPENSATED",
            "failed_step": "UPDATE_QUERY_EXIT",
        }

        # Given
        payload = {
            "vehicle_num": "12가3456",
            "requested_at": "2026-03-10T12:00:00+09:00",
        }

        # When
        response = self.client.post(
            "/api/v1/parking/exits",
            data=payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="exit-idempotency-key-001",
        )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json(),
            {
                "error": {
                    "code": "conflict",
                    "message": "출차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
                    "details": {
                        "operation_id": "exit-op-001",
                        "status": "COMPENSATED",
                        "failed_step": "UPDATE_QUERY_EXIT",
                    },
                }
            },
        )

    @patch("orchestration_service.views.OperationStatusQueryService")
    def test_should_match_saga_status_response_schema__when_operation_status_is_requested(
        self,
        operation_status_query_service_class,
    ) -> None:
        """[CT-OR-API-03] 사가 상태 조회 계약"""

        operation_status_query_service_class.return_value.get.return_value = {
            "operation_id": "entry-op-001",
            "saga_type": "ENTRY",
            "status": "FAILED",
            "current_step": "UPDATE_QUERY_ENTRY",
            "history_id": 101,
            "vehicle_num": "12가3456",
            "slot_id": 7,
            "last_error_code": "projection_update_failed",
            "last_error_message": "parking-query-service timeout",
        }

        # Given
        operation_id = "entry-op-001"

        # When
        response = self.client.get(f"/api/v1/saga-operations/{operation_id}")

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "operation_id": "entry-op-001",
                "saga_type": "ENTRY",
                "status": "FAILED",
                "current_step": "UPDATE_QUERY_ENTRY",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "last_error_code": "projection_update_failed",
                "last_error_message": "parking-query-service timeout",
            },
        )
