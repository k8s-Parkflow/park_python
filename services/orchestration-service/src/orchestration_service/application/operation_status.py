from orchestration_service.repositories.operation import SagaOperationRepository


class OperationStatusQueryService:
    def __init__(self) -> None:
        self.operation_repository = SagaOperationRepository()

    def get(self, *, operation_id: str) -> dict:
        operation = self.operation_repository.get(operation_id=operation_id)
        return {
            "operation_id": operation.operation_id,
            "saga_type": operation.saga_type,
            "status": operation.status,
            "current_step": operation.current_step,
            "failed_step": operation.failed_step,
            "history_id": operation.history_id,
            "vehicle_num": operation.vehicle_num,
            "slot_id": operation.slot_id,
            "last_error_code": operation.last_error_code,
            "last_error_message": operation.last_error_message,
            "compensation_attempts": operation.compensation_attempts,
            "next_retry_at": operation.next_retry_at.isoformat() if operation.next_retry_at else None,
            "expires_at": operation.expires_at.isoformat() if operation.expires_at else None,
            "cancelled_at": operation.cancelled_at.isoformat() if operation.cancelled_at else None,
        }
