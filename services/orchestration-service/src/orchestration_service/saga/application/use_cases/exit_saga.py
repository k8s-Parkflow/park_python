from __future__ import annotations

import uuid

from orchestration_service.constants import (
    COMPENSATE_PARKING_EXIT,
    COMPENSATE_QUERY_EXIT,
    EXIT_SAGA_TYPE,
    STATUS_IN_PROGRESS,
    STEP_PARKING_COMMAND_EXIT,
    STEP_UPDATE_QUERY_EXIT,
    STEP_VALIDATE_ACTIVE_PARKING,
)
from orchestration_service.saga.application.errors import DownstreamError
from orchestration_service.saga.application.result_factory import (
    build_compensated_result,
    build_completed_exit_result,
    build_failed_result,
)
from orchestration_service.saga.infrastructure.repositories.operation import (
    SagaOperationRepository,
)


class ExitSagaOrchestrationService:
    def __init__(
        self,
        *,
        operation_repository: SagaOperationRepository,
        zone_gateway,
        parking_command_gateway,
        parking_query_gateway,
    ) -> None:
        self.operation_repository = operation_repository
        self.zone_gateway = zone_gateway
        self.parking_command_gateway = parking_command_gateway
        self.parking_query_gateway = parking_query_gateway

    def execute(
        self,
        *,
        vehicle_num: str,
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
            saga_type=EXIT_SAGA_TYPE,
            status=STATUS_IN_PROGRESS,
            current_step=STEP_VALIDATE_ACTIVE_PARKING,
            idempotency_key=idempotency_key,
            vehicle_num=vehicle_num,
        )

        active_parking = None
        exit_payload = None
        zone_name = ""

        try:
            active_parking = self.parking_command_gateway.validate_active_parking(
                vehicle_num=vehicle_num
            )
            self.operation_repository.mark_step(
                operation_id=operation_id,
                current_step=STEP_PARKING_COMMAND_EXIT,
                history_id=active_parking["history_id"],
                slot_id=active_parking["slot_id"],
                vehicle_num=active_parking["vehicle_num"],
            )
            exit_payload = self.parking_command_gateway.exit_parking(
                operation_id=operation_id,
                vehicle_num=vehicle_num,
                requested_at=requested_at,
            )
            self.operation_repository.mark_step(
                operation_id=operation_id,
                current_step=STEP_UPDATE_QUERY_EXIT,
                history_id=exit_payload["history_id"],
                slot_id=exit_payload["slot_id"],
                vehicle_num=exit_payload["vehicle_num"],
            )
            self.parking_query_gateway.apply_exit_projection(
                operation_id=operation_id,
                history_id=exit_payload["history_id"],
                vehicle_num=exit_payload["vehicle_num"],
                slot_id=exit_payload["slot_id"],
                slot_code=active_parking["slot_code"],
                zone_id=active_parking["zone_id"],
                slot_type=active_parking["slot_type"],
                exit_at=exit_payload["exit_at"],
            )
        except DownstreamError as error:
            if exit_payload is None:
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

            zone_name = active_parking.get("zone_name", "")
            if not zone_name:
                zone_payload = self.zone_gateway.get_zone(zone_id=active_parking["zone_id"])
                zone_name = zone_payload["zone_name"]

            self.parking_query_gateway.compensate_exit_projection(
                operation_id=operation_id,
                history_id=exit_payload["history_id"],
                vehicle_num=exit_payload["vehicle_num"],
                slot_id=exit_payload["slot_id"],
                slot_code=active_parking["slot_code"],
                zone_id=active_parking["zone_id"],
                zone_name=zone_name,
                slot_type=active_parking["slot_type"],
                entry_at=active_parking["entry_at"],
            )
            self.parking_command_gateway.compensate_exit(
                operation_id=operation_id,
                history_id=exit_payload["history_id"],
                slot_id=exit_payload["slot_id"],
                vehicle_num=exit_payload["vehicle_num"],
            )
            result = build_compensated_result(
                operation_id=operation_id,
                failed_step=STEP_UPDATE_QUERY_EXIT,
                error_message="출차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
            )
            self.operation_repository.compensate(
                operation_id=operation_id,
                failed_step=STEP_UPDATE_QUERY_EXIT,
                last_error_code=error.error_code,
                last_error_message=error.message,
                completed_compensations=[
                    COMPENSATE_QUERY_EXIT,
                    COMPENSATE_PARKING_EXIT,
                ],
                result_snapshot=result,
            )
            return result

        result = build_completed_exit_result(
            operation_id=operation_id,
            exit_payload=exit_payload,
        )
        self.operation_repository.complete(
            operation_id=operation_id,
            current_step=STEP_UPDATE_QUERY_EXIT,
            result_snapshot=result,
        )
        return result
