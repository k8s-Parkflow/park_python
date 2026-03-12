from __future__ import annotations

import json
from http import HTTPStatus

from django.http import HttpRequest, JsonResponse

from orchestration_service.saga.bootstrap import (
    build_entry_saga_service,
    build_exit_saga_service,
    build_operation_status_query_service,
)
from shared.error_handling.error_codes import ErrorCode
from shared.error_handling.responses import build_error_response


def _load_json_body(request: HttpRequest) -> dict:
    return json.loads(request.body or "{}")


def _missing_idempotency_key_response() -> JsonResponse:
    return build_error_response(
        code=ErrorCode.BAD_REQUEST,
        status=HTTPStatus.BAD_REQUEST,
        details={"Idempotency-Key": ["헤더가 필요합니다."]},
    )


def _build_failed_response(result: dict) -> JsonResponse:
    return build_error_response(
        code=result["error_code"],
        message=result["error_message"],
        status=result["error_status"],
        details={
            "operation_id": result["operation_id"],
            "status": result["status"],
            "failed_step": result["failed_step"],
        },
    )


def create_entry(request: HttpRequest) -> JsonResponse:
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return _missing_idempotency_key_response()

    payload = _load_json_body(request)
    result = build_entry_saga_service().execute(
        vehicle_num=payload["vehicle_num"],
        slot_id=payload["slot_id"],
        requested_at=payload["requested_at"],
        idempotency_key=idempotency_key,
    )
    if result["status"] == "COMPLETED":
        return JsonResponse(result, status=201)
    return _build_failed_response(result)


def create_exit(request: HttpRequest) -> JsonResponse:
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return _missing_idempotency_key_response()

    payload = _load_json_body(request)
    result = build_exit_saga_service().execute(
        vehicle_num=payload["vehicle_num"],
        requested_at=payload["requested_at"],
        idempotency_key=idempotency_key,
    )
    if result["status"] == "COMPLETED":
        return JsonResponse(result, status=200)
    return _build_failed_response(result)


def get_saga_operation(_request: HttpRequest, operation_id: str) -> JsonResponse:
    payload = build_operation_status_query_service().get(operation_id=operation_id)
    return JsonResponse(payload, status=200)
