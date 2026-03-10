from __future__ import annotations

from orchestration_service.models import SagaOperation


class SagaOperationRepository:
    def get(self, *, operation_id: str) -> SagaOperation:
        return SagaOperation.objects.get(operation_id=operation_id)

    def find_by_idempotency_key(self, *, idempotency_key: str) -> SagaOperation | None:
        return SagaOperation.objects.filter(idempotency_key=idempotency_key).first()

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

    def mark_in_progress(
        self,
        *,
        operation_id: str,
        current_step: str,
        history_id: int | None = None,
        slot_id: int | None = None,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "IN_PROGRESS"
        operation.current_step = current_step
        operation.history_id = history_id or operation.history_id
        operation.slot_id = slot_id or operation.slot_id
        operation.save(update_fields=["status", "current_step", "history_id", "slot_id", "updated_at"])
        return operation

    def mark_completed(
        self,
        *,
        operation_id: str,
        current_step: str,
        history_id: int | None = None,
        slot_id: int | None = None,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "COMPLETED"
        operation.current_step = current_step
        operation.history_id = history_id or operation.history_id
        operation.slot_id = slot_id or operation.slot_id
        operation.save(update_fields=["status", "current_step", "history_id", "slot_id", "updated_at"])
        return operation

    def mark_failed(self, *, operation_id: str, failed_step: str, error_payload: dict) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "FAILED"
        operation.current_step = failed_step
        operation.last_error_code = error_payload.get("error", {}).get("code")
        operation.last_error_message = error_payload.get("error", {}).get("message")
        operation.save(
            update_fields=["status", "current_step", "last_error_code", "last_error_message", "updated_at"]
        )
        return operation

    def mark_compensated(
        self,
        *,
        operation_id: str,
        failed_step: str,
        error_payload: dict,
    ) -> SagaOperation:
        operation = self.get(operation_id=operation_id)
        operation.status = "COMPENSATED"
        operation.current_step = failed_step
        operation.last_error_code = error_payload.get("error", {}).get("code")
        operation.last_error_message = error_payload.get("error", {}).get("message")
        operation.save(
            update_fields=["status", "current_step", "last_error_code", "last_error_message", "updated_at"]
        )
        return operation

    def to_response(self, operation: SagaOperation) -> dict:
        response = {
            "operation_id": operation.operation_id,
            "status": operation.status,
        }
        if operation.history_id is not None:
            response["history_id"] = operation.history_id
        if operation.vehicle_num is not None:
            response["vehicle_num"] = operation.vehicle_num
        if operation.slot_id is not None:
            response["slot_id"] = operation.slot_id
        if operation.last_error_code is not None:
            response["last_error_code"] = operation.last_error_code
        if operation.last_error_message is not None:
            response["last_error_message"] = operation.last_error_message
        return response
