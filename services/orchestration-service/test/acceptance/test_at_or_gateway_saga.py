import sys
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


@override_settings(ROOT_URLCONF="orchestration_service.urls")
class OrchestrationGatewayAcceptanceTests(TestCase):
    @patch("orchestration_service.views.EntrySagaOrchestrationService")
    def test_should_complete_entry_saga_via_gateway__when_dependencies_succeed(
        self,
        entry_saga_service_class,
    ) -> None:
        """[AT-OR-ENTRY-01] 입차 성공"""

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
        self.assertJSONEqual(
            response.content,
            {
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "entry_at": "2026-03-10T10:00:00+09:00",
            },
        )
        entry_saga_service_class.return_value.execute.assert_called_once_with(
            vehicle_num="12가3456",
            slot_id=7,
            requested_at="2026-03-10T10:00:00+09:00",
            idempotency_key="entry-idempotency-key-001",
        )

    @patch("orchestration_service.views.EntrySagaOrchestrationService")
    def test_should_return_failed_saga_payload__when_entry_projection_update_fails(
        self,
        entry_saga_service_class,
    ) -> None:
        """[AT-OR-ENTRY-02] 입차 중 projection 실패 시 보상"""

        entry_saga_service_class.return_value.execute.return_value = {
            "operation_id": "entry-op-002",
            "status": "COMPENSATED",
            "failed_step": "UPDATE_QUERY_ENTRY",
        }

        # Given
        payload = {
            "vehicle_num": "12가3456",
            "slot_id": 8,
            "requested_at": "2026-03-10T10:05:00+09:00",
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
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "conflict",
                    "message": "입차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
                    "details": {
                        "operation_id": "entry-op-002",
                        "status": "COMPENSATED",
                        "failed_step": "UPDATE_QUERY_ENTRY",
                    },
                }
            },
        )

    @patch("orchestration_service.views.EntrySagaOrchestrationService")
    def test_should_return_internal_error_payload__when_entry_compensation_is_cancelled(
        self,
        entry_saga_service_class,
    ) -> None:
        """[AT-OR-ENTRY-05] 입차 보상 취소 응답"""

        entry_saga_service_class.return_value.execute.return_value = {
            "operation_id": "entry-op-003",
            "status": "CANCELLED",
            "failed_step": "UPDATE_QUERY_ENTRY",
        }

        # Given
        payload = {
            "vehicle_num": "12가3456",
            "slot_id": 8,
            "requested_at": "2026-03-10T10:05:00+09:00",
        }

        # When
        response = self.client.post(
            "/api/v1/parking/entries",
            data=payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-003",
        )

        # Then
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "보상 트랜잭션이 제한 시간 내 완료되지 않아 사가가 취소되었습니다.",
                    "details": {
                        "operation_id": "entry-op-003",
                        "status": "CANCELLED",
                        "failed_step": "UPDATE_QUERY_ENTRY",
                    },
                }
            },
        )

    @patch("orchestration_service.views.ExitSagaOrchestrationService")
    def test_should_complete_exit_saga_via_gateway__when_dependencies_succeed(
        self,
        exit_saga_service_class,
    ) -> None:
        """[AT-OR-EXIT-01] 출차 성공"""

        exit_saga_service_class.return_value.execute.return_value = {
            "operation_id": "exit-op-001",
            "status": "COMPLETED",
            "history_id": 101,
            "vehicle_num": "12가3456",
            "slot_id": 7,
            "exit_at": "2026-03-10T12:00:00+09:00",
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
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "operation_id": "exit-op-001",
                "status": "COMPLETED",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "exit_at": "2026-03-10T12:00:00+09:00",
            },
        )
        exit_saga_service_class.return_value.execute.assert_called_once_with(
            vehicle_num="12가3456",
            requested_at="2026-03-10T12:00:00+09:00",
            idempotency_key="exit-idempotency-key-001",
        )

    @patch("orchestration_service.views.EntrySagaOrchestrationService")
    def test_should_return_bad_request__when_entry_idempotency_key_is_missing(
        self,
        entry_saga_service_class,
    ) -> None:
        """[AT-OR-ENTRY-06] 입차 헤더 누락 검증"""

        response = self.client.post(
            "/api/v1/parking/entries",
            data={
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "requested_at": "2026-03-10T10:00:00+09:00",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"missing_header": "Idempotency-Key"},
                }
            },
        )
        entry_saga_service_class.return_value.execute.assert_not_called()

    @patch("orchestration_service.views.ExitSagaOrchestrationService")
    def test_should_return_bad_request__when_exit_payload_is_incomplete(
        self,
        exit_saga_service_class,
    ) -> None:
        """[AT-OR-EXIT-02] 출차 필수 필드 누락"""

        response = self.client.post(
            "/api/v1/parking/exits",
            data={"vehicle_num": "12가3456"},
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="exit-idempotency-key-002",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"missing_fields": ["requested_at"]},
                }
            },
        )
        exit_saga_service_class.return_value.execute.assert_not_called()

    @patch("orchestration_service.views.EntrySagaOrchestrationService")
    def test_should_return_bad_request__when_entry_body_is_not_valid_json(
        self,
        entry_saga_service_class,
    ) -> None:
        """[AT-OR-ENTRY-07] 입차 malformed JSON"""

        response = self.client.post(
            "/api/v1/parking/entries",
            data='{"vehicle_num": "12가3456"',
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="entry-idempotency-key-004",
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "JSON 형식이 올바르지 않습니다.",
                }
            },
        )
        entry_saga_service_class.return_value.execute.assert_not_called()

    @patch("orchestration_service.views.OperationStatusQueryService")
    def test_should_return_saga_status__when_operation_status_is_requested(
        self,
        operation_status_query_service_class,
    ) -> None:
        """[AT-OR-CORE-01] 사가 상태 조회"""

        operation_status_query_service_class.return_value.get.return_value = {
            "operation_id": "entry-op-001",
            "saga_type": "ENTRY",
            "status": "COMPENSATED",
            "current_step": "COMPENSATE_PARKING_ENTRY",
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
        self.assertJSONEqual(
            response.content,
            {
                "operation_id": "entry-op-001",
                "saga_type": "ENTRY",
                "status": "COMPENSATED",
                "current_step": "COMPENSATE_PARKING_ENTRY",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "last_error_code": "projection_update_failed",
                "last_error_message": "parking-query-service timeout",
            },
        )
        operation_status_query_service_class.return_value.get.assert_called_once_with(
            operation_id="entry-op-001",
        )
