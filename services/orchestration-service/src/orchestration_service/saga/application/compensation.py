from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from time import sleep as default_sleep
from typing import Callable

from django.utils import timezone

from orchestration_service.saga.infrastructure.clients.http import DownstreamHttpError
from orchestration_service.saga.infrastructure.repositories.operation import (
    SagaOperationRepository,
)
from park_py.error_handling import ApplicationError
from park_py.error_handling.error_codes import serialize_error_code


@dataclass(frozen=True)
class CompensationAction:
    step_key: str
    run: Callable[[], dict]


class CompensationRunner:
    def __init__(
        self,
        *,
        repository: SagaOperationRepository,
        clock=timezone.now,
        sleep=default_sleep,
        backoff_seconds: tuple[float, ...] = (0.1, 0.2, 0.4),
        ttl_seconds: float = 1.0,
    ) -> None:
        self.repository = repository
        self.clock = clock
        self.sleep = sleep
        self.backoff_seconds = backoff_seconds
        self.ttl_seconds = ttl_seconds

    def run(
        self,
        *,
        operation_id: str,
        failed_step: str,
        compensations: list[CompensationAction],
    ) -> dict:
        deadline = self.clock() + timedelta(seconds=self.ttl_seconds)
        attempt = 0
        last_error_payload = {"error": {}}
        completed_steps = set(self.repository.get(operation_id=operation_id).completed_compensations)

        while True:
            try:
                for compensation in compensations:
                    if compensation.step_key in completed_steps:
                        continue

                    compensation.run()
                    self.repository.mark_compensation_step_completed(
                        operation_id=operation_id,
                        step_key=compensation.step_key,
                    )
                    completed_steps.add(compensation.step_key)

                self.repository.mark_compensated(
                    operation_id=operation_id,
                    failed_step=failed_step,
                    error_payload=last_error_payload,
                    response_payload={
                        "operation_id": operation_id,
                        "status": "COMPENSATED",
                        "failed_step": failed_step,
                    },
                )
                return {
                    "operation_id": operation_id,
                    "status": "COMPENSATED",
                    "failed_step": failed_step,
                }
            except (DownstreamHttpError, ApplicationError) as exc:
                attempt += 1
                last_error_payload = self._error_payload(exc)
                next_retry_at = self.clock() + timedelta(seconds=self._backoff_for(attempt))

                if next_retry_at > deadline:
                    self.repository.mark_cancelled(
                        operation_id=operation_id,
                        failed_step=failed_step,
                        error_payload=last_error_payload,
                        response_payload={
                            "operation_id": operation_id,
                            "status": "CANCELLED",
                            "failed_step": failed_step,
                        },
                    )
                    return {
                        "operation_id": operation_id,
                        "status": "CANCELLED",
                        "failed_step": failed_step,
                    }

                self.repository.mark_compensation_retry(
                    operation_id=operation_id,
                    failed_step=failed_step,
                    error_payload=last_error_payload,
                    next_retry_at=next_retry_at,
                    expires_at=deadline,
                )
                self.sleep(self._backoff_for(attempt))

    def _backoff_for(self, attempt: int) -> float:
        index = min(attempt - 1, len(self.backoff_seconds) - 1)
        return self.backoff_seconds[index]

    def _error_payload(self, exc: DownstreamHttpError | ApplicationError) -> dict:
        if isinstance(exc, DownstreamHttpError):
            return exc.payload

        return {
            "error": {
                "code": serialize_error_code(exc.code),
                "message": exc.message,
                "details": exc.details,
            }
        }
