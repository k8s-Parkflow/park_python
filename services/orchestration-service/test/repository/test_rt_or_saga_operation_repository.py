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

        from orchestration_service.saga.domain.entities import SagaOperation

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

    def test_should_preserve_idempotency_key_uniqueness_per_saga_type__when_same_key_is_saved_twice(
        self,
    ) -> None:
        """[RT-OR-DB-02] saga_type별 idempotency_key 유일성"""

        from orchestration_service.saga.domain.entities import SagaOperation

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

    def test_should_allow_same_idempotency_key_across_different_saga_types(self) -> None:
        """[RT-OR-DB-03] saga_type 분리 멱등키 허용"""

        from orchestration_service.saga.domain.entities import SagaOperation

        SagaOperation.objects.create(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="COMPLETED",
            idempotency_key="shared-idempotency-key-001",
        )

        saved = SagaOperation.objects.create(
            operation_id="exit-op-001",
            saga_type="EXIT",
            status="COMPLETED",
            idempotency_key="shared-idempotency-key-001",
        )

        self.assertEqual(saved.operation_id, "exit-op-001")

    def test_should_persist_recovery_fields__when_saga_state_is_saved(self) -> None:
        """[RT-OR-DB-04] 상태 복구 필드 저장"""

        from orchestration_service.saga.infrastructure.repositories.operation import (
            SagaOperationRepository,
        )

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

    def test_should_return_snapshot_payload__when_completed_response_is_replayed(self) -> None:
        """[RT-OR-DB-05] 응답 snapshot 재사용"""

        from orchestration_service.saga.infrastructure.repositories.operation import (
            SagaOperationRepository,
        )

        repository = SagaOperationRepository()
        operation = repository.save(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="IN_PROGRESS",
            current_step="PARKING_COMMAND_ENTRY",
            idempotency_key="entry-idempotency-key-001",
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
        )

        repository.mark_completed(
            operation_id=operation.operation_id,
            current_step="UPDATE_QUERY_ENTRY",
            history_id=101,
            slot_id=7,
            response_payload={
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "entry_at": "2026-03-10T10:00:00+09:00",
            },
        )

        saved = repository.get(operation_id="entry-op-001")

        self.assertEqual(
            repository.to_response(saved),
            {
                "operation_id": "entry-op-001",
                "status": "COMPLETED",
                "history_id": 101,
                "vehicle_num": "12가3456",
                "slot_id": 7,
                "entry_at": "2026-03-10T10:00:00+09:00",
            },
        )

    def test_should_find_existing_operation_only_with_same_saga_type(self) -> None:
        """[RT-OR-DB-06] saga_type 기준 멱등 조회"""

        from orchestration_service.saga.infrastructure.repositories.operation import (
            SagaOperationRepository,
        )

        repository = SagaOperationRepository()
        repository.save(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="COMPLETED",
            idempotency_key="shared-idempotency-key-001",
        )
        repository.save(
            operation_id="exit-op-001",
            saga_type="EXIT",
            status="COMPLETED",
            idempotency_key="shared-idempotency-key-001",
        )

        entry_operation = repository.find_by_idempotency_key(
            saga_type="ENTRY",
            idempotency_key="shared-idempotency-key-001",
        )
        exit_operation = repository.find_by_idempotency_key(
            saga_type="EXIT",
            idempotency_key="shared-idempotency-key-001",
        )

        self.assertIsNotNone(entry_operation)
        self.assertIsNotNone(exit_operation)
        self.assertEqual(entry_operation.operation_id, "entry-op-001")
        self.assertEqual(exit_operation.operation_id, "exit-op-001")
