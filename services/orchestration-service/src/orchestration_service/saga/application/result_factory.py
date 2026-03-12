from __future__ import annotations

from orchestration_service.constants import STATUS_COMPENSATED, STATUS_COMPLETED, STATUS_FAILED


def build_failed_result(
    *,
    operation_id: str,
    failed_step: str,
    error_status: int,
    error_code: str,
    error_message: str,
) -> dict:
    return {
        "operation_id": operation_id,
        "status": STATUS_FAILED,
        "failed_step": failed_step,
        "error_status": error_status,
        "error_code": error_code,
        "error_message": error_message,
    }


def build_compensated_result(
    *,
    operation_id: str,
    failed_step: str,
    error_message: str,
) -> dict:
    return {
        "operation_id": operation_id,
        "status": STATUS_COMPENSATED,
        "failed_step": failed_step,
        "error_status": 409,
        "error_code": "conflict",
        "error_message": error_message,
    }


def build_completed_entry_result(*, operation_id: str, entry_payload: dict) -> dict:
    return {
        "operation_id": operation_id,
        "status": STATUS_COMPLETED,
        "history_id": entry_payload["history_id"],
        "vehicle_num": entry_payload["vehicle_num"],
        "slot_id": entry_payload["slot_id"],
        "entry_at": entry_payload["entry_at"],
    }


def build_completed_exit_result(*, operation_id: str, exit_payload: dict) -> dict:
    return {
        "operation_id": operation_id,
        "status": STATUS_COMPLETED,
        "history_id": exit_payload["history_id"],
        "vehicle_num": exit_payload["vehicle_num"],
        "slot_id": exit_payload["slot_id"],
        "exit_at": exit_payload["exit_at"],
    }
