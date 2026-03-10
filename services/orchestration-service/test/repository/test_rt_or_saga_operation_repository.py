import sys
from pathlib import Path

from django.db import IntegrityError
from django.test import TestCase


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationSagaOperationRepositoryTests(TestCase):
    def test_should_fail_duplicate_operation_id_persist__when_same_operation_id_is_saved(
        self,
    ) -> None:
        """[RT-OR-DB-01] operation_id 유일성"""

        from orchestration_service.models import SagaOperation

        # Given
        SagaOperation.objects.create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="IN_PROGRESS",
            idempotency_key="entry-idempotency-key-001",
        )

        # When / Then
        with self.assertRaises(IntegrityError):
            SagaOperation.objects.create(
                operation_id="entry-op-001",
                saga_type="ENTRY",
                status="IN_PROGRESS",
                idempotency_key="entry-idempotency-key-002",
            )

    def test_should_preserve_idempotency_key_uniqueness__when_same_key_is_saved_twice(
        self,
    ) -> None:
        """[RT-OR-DB-02] idempotency_key 유일성"""

        from orchestration_service.models import SagaOperation

        # Given
        SagaOperation.objects.create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="COMPLETED",
            idempotency_key="entry-idempotency-key-001",
        )

        # When / Then
        with self.assertRaises(IntegrityError):
            SagaOperation.objects.create(
                operation_id="entry-op-002",
                saga_type="ENTRY",
                status="IN_PROGRESS",
                idempotency_key="entry-idempotency-key-001",
            )

    def test_should_persist_recovery_fields__when_saga_state_is_saved(self) -> None:
        """[RT-OR-DB-03] 상태 복구 필드 저장"""

        from orchestration_service.repositories.operation import SagaOperationRepository

        # Given
        repository = SagaOperationRepository()

        # When
        saved = repository.save(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="FAILED",
            current_step="UPDATE_QUERY_ENTRY",
            idempotency_key="entry-idempotency-key-001",
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            last_error_code="projection_update_failed",
            last_error_message="parking-query-service timeout",
        )

        # Then
        self.assertEqual(saved.operation_id, "entry-op-001")
        self.assertEqual(saved.current_step, "UPDATE_QUERY_ENTRY")
        self.assertEqual(saved.history_id, 101)
        self.assertEqual(saved.vehicle_num, "12가3456")
        self.assertEqual(saved.slot_id, 7)
        self.assertEqual(saved.last_error_code, "projection_update_failed")
        self.assertEqual(saved.last_error_message, "parking-query-service timeout")
