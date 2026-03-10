from typing import Any


class EntrySagaOrchestrationService:
    def execute(
        self,
        *,
        vehicle_num: str,
        slot_id: int,
        requested_at: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        raise NotImplementedError


class ExitSagaOrchestrationService:
    def execute(
        self,
        *,
        vehicle_num: str,
        requested_at: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        raise NotImplementedError


class OperationStatusQueryService:
    def get(self, *, operation_id: str) -> dict[str, Any]:
        raise NotImplementedError

