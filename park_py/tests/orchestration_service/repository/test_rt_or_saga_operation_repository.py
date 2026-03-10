from __future__ import annotations

from django.db import IntegrityError
from django.test import TestCase

from orchestration_service.models import SagaOperation
from orchestration_service.repositories.operation import SagaOperationRepository


class OrchestrationSagaOperationRepositoryTests(TestCase):
    def test_should_fail_duplicate_operation_id_persist__when_same_operation_id_is_saved(
        self,
    ) -> None:
        """[RT-OR-DB-01] operation_id 유일성"""

        SagaOperation.objects.create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="IN_PROGRESS",
            current_step="VALIDATE_VEHICLE",
            idempotency_key="entry-idempotency-key-001",
        )

        with self.assertRaises(IntegrityError):
            SagaOperation.objects.create(
                operation_id="entry-op-001",
                saga_type="ENTRY",
                status="IN_PROGRESS",
                current_step="VALIDATE_VEHICLE",
                idempotency_key="entry-idempotency-key-002",
            )

    def test_should_preserve_idempotency_key_uniqueness__when_same_key_is_saved_twice(
        self,
    ) -> None:
        """[RT-OR-DB-02] idempotency_key 유일성"""

        SagaOperation.objects.create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="COMPLETED",
            current_step="UPDATE_QUERY_ENTRY",
            idempotency_key="entry-idempotency-key-001",
        )

        with self.assertRaises(IntegrityError):
            SagaOperation.objects.create(
                operation_id="entry-op-002",
                saga_type="ENTRY",
                status="IN_PROGRESS",
                current_step="VALIDATE_VEHICLE",
                idempotency_key="entry-idempotency-key-001",
            )

    def test_should_persist_recovery_fields__when_saga_state_is_saved(self) -> None:
        """[RT-OR-DB-03] 상태 복구 필드 저장"""

        saved = SagaOperationRepository().create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="FAILED",
            current_step="UPDATE_QUERY_ENTRY",
            idempotency_key="entry-idempotency-key-001",
            vehicle_num="12가3456",
            slot_id=7,
        )
        SagaOperationRepository().fail(
            operation_id=saved.operation_id,
            last_error_code="projection_update_failed",
            last_error_message="parking-query-service timeout",
            result_snapshot={"status": "FAILED"},
        )

        refreshed = SagaOperation.objects.get(operation_id="entry-op-001")
        self.assertEqual(refreshed.current_step, "UPDATE_QUERY_ENTRY")
        self.assertEqual(refreshed.vehicle_num, "12가3456")
        self.assertEqual(refreshed.slot_id, 7)
        self.assertEqual(refreshed.last_error_code, "projection_update_failed")
        self.assertEqual(refreshed.last_error_message, "parking-query-service timeout")
