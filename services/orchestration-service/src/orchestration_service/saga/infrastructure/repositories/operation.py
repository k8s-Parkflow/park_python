from __future__ import annotations

from django.utils import timezone

from orchestration_service.saga.domain.entities import SagaOperation


class SagaOperationRepository:
    def _persist(self, operation: SagaOperation, *, update_fields: list[str]) -> SagaOperation:
        operation.save(update_fields=[*update_fields, "updated_at"])
        return operation

    def create(
        self,
        *,
        operation_id: str,
        saga_type: str,
        status: str,
        current_step: str,
        idempotency_key: str,
        vehicle_num: str = "",
        slot_id: int | None = None,
    ) -> SagaOperation:
        return SagaOperation.objects.create(
            operation_id=operation_id,
            saga_type=saga_type,
            status=status,
            current_step=current_step,
            idempotency_key=idempotency_key,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
        )

    def find_by_idempotency_key(self, *, idempotency_key: str) -> SagaOperation | None:
        return SagaOperation.objects.filter(idempotency_key=idempotency_key).first()

    def get(self, *, operation_id: str) -> SagaOperation:
        return SagaOperation.objects.get(operation_id=operation_id)

    def mark_step(
        self,
        *,
        operation_id: str,
        current_step: str,
        history_id: int | None = None,
        slot_id: int | None = None,
        vehicle_num: str | None = None,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.current_step = current_step
        if history_id is not None:
            operation.history_id = history_id
        if slot_id is not None:
            operation.slot_id = slot_id
        if vehicle_num is not None:
            operation.vehicle_num = vehicle_num
        return self._persist(
            operation,
            update_fields=["current_step", "history_id", "slot_id", "vehicle_num"],
        )

    def complete(
        self,
        *,
        operation_id: str,
        current_step: str,
        result_snapshot: dict,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "COMPLETED"
        operation.current_step = current_step
        operation.result_snapshot = result_snapshot
        operation.completed_at = timezone.now()
        return self._persist(
            operation,
            update_fields=[
                "status",
                "current_step",
                "result_snapshot",
                "completed_at",
            ],
        )

    def fail(
        self,
        *,
        operation_id: str,
        last_error_code: str,
        last_error_message: str,
        result_snapshot: dict,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "FAILED"
        operation.last_error_code = last_error_code
        operation.last_error_message = last_error_message
        operation.result_snapshot = result_snapshot
        return self._persist(
            operation,
            update_fields=[
                "status",
                "last_error_code",
                "last_error_message",
                "result_snapshot",
            ],
        )

    def compensate(
        self,
        *,
        operation_id: str,
        failed_step: str,
        last_error_code: str,
        last_error_message: str,
        completed_compensations: list[str],
        result_snapshot: dict,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "COMPENSATED"
        operation.current_step = failed_step
        operation.last_error_code = last_error_code
        operation.last_error_message = last_error_message
        operation.completed_compensations = completed_compensations
        operation.result_snapshot = result_snapshot
        operation.completed_at = timezone.now()
        return self._persist(
            operation,
            update_fields=[
                "status",
                "current_step",
                "last_error_code",
                "last_error_message",
                "completed_compensations",
                "result_snapshot",
                "completed_at",
            ],
        )
