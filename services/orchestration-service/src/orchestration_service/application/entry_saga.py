from __future__ import annotations

import uuid

from orchestration_service.application.errors import DownstreamError
from orchestration_service.application.result_factory import (
    build_compensated_result,
    build_completed_entry_result,
    build_failed_result,
)
from orchestration_service.constants import (
    COMPENSATE_PARKING_ENTRY,
    COMPENSATE_QUERY_ENTRY,
    ENTRY_SAGA_TYPE,
    STATUS_IN_PROGRESS,
    STEP_PARKING_COMMAND_ENTRY,
    STEP_UPDATE_QUERY_ENTRY,
    STEP_VALIDATE_VEHICLE,
    STEP_VALIDATE_ZONE_POLICY,
)
from orchestration_service.repositories.operation import SagaOperationRepository


class EntrySagaOrchestrationService:
    def __init__(
        self,
        *,
        operation_repository: SagaOperationRepository,
        vehicle_gateway,
        zone_gateway,
        parking_command_gateway,
        parking_query_gateway,
    ) -> None:
        self.operation_repository = operation_repository
        self.vehicle_gateway = vehicle_gateway
        self.zone_gateway = zone_gateway
        self.parking_command_gateway = parking_command_gateway
        self.parking_query_gateway = parking_query_gateway

    def execute(
        self,
        *,
        vehicle_num: str,
        slot_id: int,
        requested_at: str,
        idempotency_key: str,
    ) -> dict:
        existing_operation = self.operation_repository.find_by_idempotency_key(
            idempotency_key=idempotency_key
        )
        reused_operation = existing_operation and existing_operation.result_snapshot
        if reused_operation:
            return existing_operation.result_snapshot

        operation_id = uuid.uuid4().hex
        self.operation_repository.create(
            operation_id=operation_id,
            saga_type=ENTRY_SAGA_TYPE,
            status=STATUS_IN_PROGRESS,
            current_step=STEP_VALIDATE_VEHICLE,
            idempotency_key=idempotency_key,
            vehicle_num=vehicle_num,
            slot_id=slot_id,
        )

        zone_payload = None
        entry_payload = None

        try:
            vehicle_payload = self.vehicle_gateway.get_vehicle(vehicle_num=vehicle_num)
            self.operation_repository.mark_step(
                operation_id=operation_id,
                current_step=STEP_VALIDATE_ZONE_POLICY,
            )
            zone_payload = self.zone_gateway.validate_entry_policy(
                slot_id=slot_id,
                vehicle_type=vehicle_payload["vehicle_type"],
            )
            self.operation_repository.mark_step(
                operation_id=operation_id,
                current_step=STEP_PARKING_COMMAND_ENTRY,
            )
            entry_payload = self.parking_command_gateway.create_entry(
                operation_id=operation_id,
                vehicle_num=vehicle_num,
                slot_id=slot_id,
                requested_at=requested_at,
            )
            self.operation_repository.mark_step(
                operation_id=operation_id,
                current_step=STEP_UPDATE_QUERY_ENTRY,
                history_id=entry_payload["history_id"],
                slot_id=entry_payload["slot_id"],
                vehicle_num=entry_payload["vehicle_num"],
            )
            self.parking_query_gateway.apply_entry_projection(
                operation_id=operation_id,
                history_id=entry_payload["history_id"],
                vehicle_num=entry_payload["vehicle_num"],
                slot_id=entry_payload["slot_id"],
                slot_code=entry_payload["slot_code"],
                zone_id=zone_payload["zone_id"],
                slot_type=zone_payload["slot_type"],
                entry_at=entry_payload["entry_at"],
            )
        except DownstreamError as error:
            if entry_payload is None:
                result = build_failed_result(
                    operation_id=operation_id,
                    failed_step=self.operation_repository.get(operation_id=operation_id).current_step,
                    error_status=error.status,
                    error_code=error.error_code,
                    error_message=error.message,
                )
                self.operation_repository.fail(
                    operation_id=operation_id,
                    last_error_code=error.error_code,
                    last_error_message=error.message,
                    result_snapshot=result,
                )
                return result

            self.parking_query_gateway.compensate_entry_projection(
                operation_id=operation_id,
                history_id=entry_payload["history_id"],
                vehicle_num=entry_payload["vehicle_num"],
                zone_id=zone_payload["zone_id"],
                slot_type=zone_payload["slot_type"],
            )
            self.parking_command_gateway.compensate_entry(
                operation_id=operation_id,
                history_id=entry_payload["history_id"],
                slot_id=entry_payload["slot_id"],
                vehicle_num=entry_payload["vehicle_num"],
            )
            result = build_compensated_result(
                operation_id=operation_id,
                failed_step=STEP_UPDATE_QUERY_ENTRY,
                error_message="입차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
            )
            self.operation_repository.compensate(
                operation_id=operation_id,
                failed_step=STEP_UPDATE_QUERY_ENTRY,
                last_error_code=error.error_code,
                last_error_message=error.message,
                completed_compensations=[
                    COMPENSATE_QUERY_ENTRY,
                    COMPENSATE_PARKING_ENTRY,
                ],
                result_snapshot=result,
            )
            return result

        result = build_completed_entry_result(
            operation_id=operation_id,
            entry_payload=entry_payload,
        )
        self.operation_repository.complete(
            operation_id=operation_id,
            current_step=STEP_UPDATE_QUERY_ENTRY,
            result_snapshot=result,
        )
        return result
