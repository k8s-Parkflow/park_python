from __future__ import annotations

import sys
from pathlib import Path

from django.test import TestCase
from django.utils import timezone


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationCompensationStateRepositoryTests(TestCase):
    def test_should_persist_compensation_retry_state__when_retry_is_scheduled(self) -> None:
        """[RT-OR-COMP-01] 보상 재시도 상태 저장"""

        from orchestration_service.saga.domain.entities import SagaOperation
        from orchestration_service.saga.infrastructure.repositories.operation import (
            SagaOperationRepository,
        )

        repository = SagaOperationRepository()
        operation = repository.save(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="IN_PROGRESS",
            idempotency_key="entry-key-001",
        )

        next_retry_at = timezone.now()

        # When
        updated = repository.mark_compensation_retry(
            operation_id=operation.operation_id,
            failed_step="UPDATE_QUERY_ENTRY",
            error_payload={"error": {"code": "dependency_timeout", "message": "timeout"}},
            next_retry_at=next_retry_at,
        )

        # Then
        saved = SagaOperation.objects.get(operation_id=operation.operation_id)
        self.assertEqual(updated.status, "COMPENSATING")
        self.assertEqual(saved.compensation_attempts, 1)
        self.assertEqual(saved.next_retry_at, next_retry_at)
        self.assertEqual(saved.current_step, "UPDATE_QUERY_ENTRY")
        self.assertEqual(saved.failed_step, "UPDATE_QUERY_ENTRY")

    def test_should_persist_cancelled_state__when_compensation_is_abandoned(self) -> None:
        """[RT-OR-COMP-02] 보상 취소 상태 저장"""

        from orchestration_service.saga.infrastructure.repositories.operation import (
            SagaOperationRepository,
        )

        repository = SagaOperationRepository()
        operation = repository.save(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="IN_PROGRESS",
            idempotency_key="entry-key-001",
        )

        # When
        updated = repository.mark_cancelled(
            operation_id=operation.operation_id,
            failed_step="UPDATE_QUERY_ENTRY",
            error_payload={"error": {"code": "dependency_timeout", "message": "timeout"}},
            response_payload={
                "operation_id": operation.operation_id,
                "status": "CANCELLED",
                "failed_step": "UPDATE_QUERY_ENTRY",
            },
        )

        # Then
        self.assertEqual(updated.status, "CANCELLED")
        self.assertIsNotNone(updated.cancelled_at)

    def test_should_persist_completed_compensation_steps__when_step_finishes(self) -> None:
        """[RT-OR-COMP-03] 완료된 보상 단계 저장"""

        from orchestration_service.saga.infrastructure.repositories.operation import (
            SagaOperationRepository,
        )

        repository = SagaOperationRepository()
        operation = repository.save(
            operation_id="entry-op-001",
            saga_type="ENTRY",
            status="COMPENSATING",
            idempotency_key="entry-key-001",
        )

        updated = repository.mark_compensation_step_completed(
            operation_id=operation.operation_id,
            step_key="REVERT_QUERY_ENTRY",
        )

        self.assertEqual(updated.completed_compensations, ["REVERT_QUERY_ENTRY"])
