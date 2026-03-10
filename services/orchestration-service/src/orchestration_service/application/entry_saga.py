from __future__ import annotations

from uuid import uuid4

from park_py.error_handling import ApplicationError, ErrorCode

from orchestration_service.application.compensation import CompensationRunner
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
        except DownstreamHttpError as exc:
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="VALIDATE_VEHICLE" if exc.dependency == "vehicle-service" else "VALIDATE_ZONE_POLICY",
                error_payload=exc.payload,
            )
            raise_application_error_from_downstream(exc)

        if not zone_policy["entry_allowed"]:
            self.operation_repository.mark_failed(
                operation_id=operation_id,
                failed_step="VALIDATE_ZONE_POLICY",
                error_payload={"error": {"code": ErrorCode.CONFLICT.code}},
            )
            raise ApplicationError(
                code=ErrorCode.CONFLICT,
                status=409,
                details={"slot_id": slot_id},
            )

        command_result = self.parking_command_client.create_entry(
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
            )
        except DownstreamHttpError as exc:
            return self.compensation_runner.run(
                operation_id=operation_id,
                failed_step="UPDATE_QUERY_ENTRY",
                compensations=[
                    lambda: self.parking_query_client.revert_entry(vehicle_num=vehicle_num),
                    lambda: self.parking_command_client.cancel_entry(history_id=command_result["history_id"]),
                ],
            )

        completed = self.operation_repository.mark_completed(
            operation_id=operation_id,
            current_step="UPDATE_QUERY_ENTRY",
            history_id=command_result["history_id"],
        )
        return {
            "operation_id": completed.operation_id,
            "status": completed.status,
            "history_id": command_result["history_id"],
            "vehicle_num": command_result["vehicle_num"],
            "slot_id": command_result["slot_id"],
            "entry_at": command_result["entry_at"],
        }
