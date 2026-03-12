from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase, override_settings


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationGatewayContractTests(SimpleTestCase):
    @patch("orchestration_service.saga.interfaces.http.views.build_entry_saga_service")
    def test_should_match_entry_gateway_response_schema__when_entry_request_succeeds(
        self,
        build_entry_saga_service,
    ) -> None:
        """[CT-OR-API-01] 입차 API 계약"""

        build_entry_saga_service.return_value.execute.return_value = {
            "operation_id": "entry-op-001",
            "status": "COMPLETED",
            "history_id": 101,
            "vehicle_num": "12가3456",
            "slot_id": 7,
            "entry_at": "2026-03-10T10:00:00+09:00",
        }

        payload = {
            "vehicle_num": "12가3456",
            "slot_id": 7,
            "requested_at": "2026-03-10T10:00:00+09:00",
        }
        response = self.client.post(
            "/api/v1/parking/entries",
            data=payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-001",
        )

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

    @patch("orchestration_service.saga.interfaces.http.views.build_exit_saga_service")
    def test_should_match_exit_gateway_error_schema__when_exit_is_compensated(
        self,
        build_exit_saga_service,
    ) -> None:
        """[CT-OR-API-02] 출차 API 계약"""

        build_exit_saga_service.return_value.execute.return_value = {
            "operation_id": "exit-op-001",
            "status": "COMPENSATED",
            "failed_step": "UPDATE_QUERY_EXIT",
            "error_status": 409,
            "error_code": "conflict",
            "error_message": "출차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
        }

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

    @patch("orchestration_service.saga.interfaces.http.views.build_operation_status_query_service")
    def test_should_match_saga_status_response_schema__when_operation_status_is_requested(
        self,
        build_operation_status_query_service,
    ) -> None:
        """[CT-OR-API-03] 사가 상태 조회 계약"""

        build_operation_status_query_service.return_value.get.return_value = {
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

        response = self.client.get("/api/v1/saga-operations/entry-op-001")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["operation_id"], "entry-op-001")
