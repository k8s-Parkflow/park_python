from __future__ import annotations

from uuid import uuid4

from park_py.error_handling import ApplicationError, ErrorCode

from orchestration_service.application.compensation import CompensationAction
from orchestration_service.application.compensation import CompensationRunner
from orchestration_service.application.errors import build_error_payload
from orchestration_service.application.errors import raise_application_error_from_payload
from orchestration_service.application.errors import raise_application_error_from_downstream
from orchestration_service.clients.http import DownstreamHttpError
from orchestration_service.clients.parking_command import ParkingCommandServiceClient
from orchestration_service.clients.parking_query import ParkingQueryServiceClient
from orchestration_service.clients.vehicle import VehicleServiceClient
from orchestration_service.clients.zone import ZoneServiceClient
from orchestration_service.repositories.operation import SagaOperationRepository


class EntrySagaOrchestrationService:
    def __init__(self, *, base_url: str) -> None:
        self.vehicle_client = VehicleServiceClient(base_url=base_url)
        self.zone_client = ZoneServiceClient(base_url=base_url)
        self.parking_command_client = ParkingCommandServiceClient(base_url=base_url)
        self.parking_query_client = ParkingQueryServiceClient(base_url=base_url)
        self.operation_repository = SagaOperationRepository()
        self.compensation_runner = CompensationRunner(repository=self.operation_repository)

    def execute(
        self,
        *,
        vehicle_num: str,
        slot_id: int,
        requested_at: str,
        idempotency_key: str,
    ) -> dict:
        existing_operation = self.operation_repository.find_by_idempotency_key(
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
            saga_type="ENTRY",
            status="IN_PROGRESS",
            current_step="VALIDATE_VEHICLE",
            idempotency_key=idempotency_key,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
        )

        try:
            self.vehicle_client.get_vehicle(vehicle_num=vehicle_num)
            zone_policy = self.zone_client.get_entry_policy(slot_id=slot_id)
        except ApplicationError as exc:
            failed_step = "VALIDATE_ZONE_POLICY" if exc.details and exc.details.get("dependency") == "zone-service" else "VALIDATE_VEHICLE"
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step=failed_step,
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
                failed_step="VALIDATE_VEHICLE" if exc.dependency == "vehicle-service" else "VALIDATE_ZONE_POLICY",
                error_payload=exc.payload,
                error_status=exc.status_code,
            )
            raise_application_error_from_downstream(exc)

        if not zone_policy["entry_allowed"]:
            error_payload = build_error_payload(code=ErrorCode.CONFLICT, details={"slot_id": slot_id})
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="VALIDATE_ZONE_POLICY",
                error_payload=error_payload,
                error_status=409,
            )
            raise ApplicationError(
                code=ErrorCode.CONFLICT,
                status=409,
                details={"slot_id": slot_id},
            )

        try:
            command_result = self.parking_command_client.create_entry(
                operation_id=operation_id,
                vehicle_num=vehicle_num,
                slot_id=slot_id,
                requested_at=requested_at,
            )
        except ApplicationError:
            command_result = self.parking_command_client.create_entry(
                operation_id=operation_id,
                vehicle_num=vehicle_num,
                slot_id=slot_id,
                requested_at=requested_at,
            )
        self.operation_repository.mark_in_progress(
            operation_id=operation_id,
            current_step="PARKING_COMMAND_ENTRY",
            history_id=command_result["history_id"],
        )

        try:
            self.parking_query_client.project_entry(
                vehicle_num=vehicle_num,
                slot_id=slot_id,
                zone_id=zone_policy["zone_id"],
                slot_type=zone_policy["slot_type"],
                entry_at=command_result["entry_at"],
                operation_id=operation_id,
            )
        except (ApplicationError, DownstreamHttpError) as exc:
            return self.compensation_runner.run(
                operation_id=operation_id,
                failed_step="UPDATE_QUERY_ENTRY",
                compensations=[
                    CompensationAction(
                        step_key="REVERT_QUERY_ENTRY",
                        run=lambda: self.parking_query_client.revert_entry(
                            operation_id=operation_id,
                            vehicle_num=vehicle_num,
                        ),
                    ),
                    CompensationAction(
                        step_key="CANCEL_PARKING_ENTRY",
                        run=lambda: self.parking_command_client.cancel_entry(
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
            "entry_at": command_result["entry_at"],
        }
        completed = self.operation_repository.mark_completed(
            operation_id=operation_id,
            current_step="UPDATE_QUERY_ENTRY",
            history_id=command_result["history_id"],
            response_payload=response_payload,
        )
        return self.operation_repository.to_response(completed)
