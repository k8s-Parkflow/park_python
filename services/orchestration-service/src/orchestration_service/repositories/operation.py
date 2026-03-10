from __future__ import annotations

from orchestration_service.models import SagaOperation


class SagaOperationRepository:
    def save(
        self,
        *,
        operation_id: str,
        saga_type: str,
        status: str,
        current_step: str | None = None,
        idempotency_key: str,
        history_id: int | None = None,
        vehicle_num: str | None = None,
        slot_id: int | None = None,
        last_error_code: str | None = None,
        last_error_message: str | None = None,
    ) -> SagaOperation:
        return SagaOperation.objects.create(
            operation_id=operation_id,
            saga_type=saga_type,
            status=status,
            current_step=current_step,
            idempotency_key=idempotency_key,
            history_id=history_id,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
            last_error_code=last_error_code,
            last_error_message=last_error_message,
        )
