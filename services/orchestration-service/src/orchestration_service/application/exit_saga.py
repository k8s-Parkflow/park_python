from __future__ import annotations

from uuid import uuid4

from park_py.error_handling import ApplicationError

from orchestration_service.application.compensation import CompensationAction
from orchestration_service.application.compensation import CompensationRunner
from orchestration_service.application.errors import build_error_payload
from orchestration_service.application.errors import raise_application_error_from_payload
from orchestration_service.application.errors import raise_application_error_from_downstream
from orchestration_service.clients.http import DownstreamHttpError
from orchestration_service.clients.parking_command import ParkingCommandServiceClient
from orchestration_service.clients.parking_query import ParkingQueryServiceClient
from orchestration_service.repositories.operation import SagaOperationRepository


class ExitSagaOrchestrationService:
    def __init__(self, *, base_url: str) -> None:
        self.parking_command_client = ParkingCommandServiceClient(base_url=base_url)
        self.parking_query_client = ParkingQueryServiceClient(base_url=base_url)
        self.operation_repository = SagaOperationRepository()
        self.compensation_runner = CompensationRunner(repository=self.operation_repository)

    def execute(
        self,
        *,
        vehicle_num: str,
        requested_at: str,
        idempotency_key: str,
    ) -> dict:
        existing_operation = self.operation_repository.find_by_idempotency_key(
            saga_type="EXIT",
            idempotency_key=idempotency_key,
        )
        if existing_operation is not None:
            if existing_operation.error_status is not None and existing_operation.error_payload is not None:
                raise_application_error_from_payload(
                    error_payload=existing_operation.error_payload,
                    status_code=existing_operation.error_status,
                )
            return self.operation_repository.to_response(existing_operation)

        operation_id = uuid4().hex
        self.operation_repository.save(
            operation_id=operation_id,
            saga_type="EXIT",
            status="IN_PROGRESS",
            current_step="VALIDATE_ACTIVE_PARKING",
            idempotency_key=idempotency_key,
            vehicle_num=vehicle_num,
        )

        try:
            projection = self.parking_query_client.get_current_parking(vehicle_num=vehicle_num)
        except ApplicationError as exc:
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="VALIDATE_ACTIVE_PARKING",
                error_payload=build_error_payload(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                ),
                error_status=exc.status,
            )
            raise
        except DownstreamHttpError as exc:
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="VALIDATE_ACTIVE_PARKING",
                error_payload=exc.payload,
                error_status=exc.status_code,
            )
            raise_application_error_from_downstream(exc)

        try:
            command_result = self.parking_command_client.create_exit(
                operation_id=operation_id,
                vehicle_num=vehicle_num,
                requested_at=requested_at,
            )
        except ApplicationError as exc:
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="PARKING_COMMAND_EXIT",
                error_payload=build_error_payload(
                    code=exc.code,
                    message=exc.message,
                    details=exc.details,
                ),
                error_status=exc.status,
            )
            raise
        except DownstreamHttpError as exc:
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="PARKING_COMMAND_EXIT",
                error_payload=exc.payload,
                error_status=exc.status_code,
            )
            raise_application_error_from_downstream(exc)

        self.operation_repository.mark_in_progress(
            operation_id=operation_id,
            current_step="PARKING_COMMAND_EXIT",
            history_id=command_result["history_id"],
            slot_id=command_result["slot_id"],
        )

        try:
            self.parking_query_client.project_exit(
                operation_id=operation_id,
                vehicle_num=vehicle_num,
            )
        except (ApplicationError, DownstreamHttpError) as exc:
            return self.compensation_runner.run(
                operation_id=operation_id,
                failed_step="UPDATE_QUERY_EXIT",
                compensations=[
                    CompensationAction(
                        step_key="RESTORE_QUERY_EXIT",
                        run=lambda: self.parking_query_client.restore_exit(
                            operation_id=operation_id,
                            vehicle_num=projection["vehicle_num"],
                            slot_id=projection["slot_id"],
                            zone_id=projection["zone_id"],
                            slot_type=projection["slot_type"],
                            entry_at=projection["entry_at"],
                        ),
                    ),
                    CompensationAction(
                        step_key="RESTORE_PARKING_EXIT",
                        run=lambda: self.parking_command_client.restore_exit(
                            operation_id=operation_id,
                            history_id=command_result["history_id"],
                        ),
                    ),
                ],
            )

        response_payload = {
            "operation_id": operation_id,
            "status": "COMPLETED",
            "history_id": command_result["history_id"],
            "vehicle_num": command_result["vehicle_num"],
            "slot_id": command_result["slot_id"],
            "exit_at": command_result["exit_at"],
        }
        completed = self.operation_repository.mark_completed(
            operation_id=operation_id,
            current_step="UPDATE_QUERY_EXIT",
            history_id=command_result["history_id"],
            slot_id=command_result["slot_id"],
            response_payload=response_payload,
        )
        return self.operation_repository.to_response(completed)
