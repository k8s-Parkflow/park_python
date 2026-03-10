import json
from http import HTTPStatus
from typing import Any

from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST

from park_py.error_handling import ErrorCode
from park_py.error_handling.responses import build_error_response

from orchestration_service.services import EntrySagaOrchestrationService
from orchestration_service.services import ExitSagaOrchestrationService
from orchestration_service.services import OperationStatusQueryService


def _decode_json_body(request: HttpRequest) -> dict[str, Any]:
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))


def _build_compensated_response(*, message: str, result: dict[str, Any]) -> JsonResponse:
    return build_error_response(
        code=ErrorCode.CONFLICT,
        message=message,
        status=HTTPStatus.CONFLICT,
        details={
            "operation_id": result["operation_id"],
            "status": result["status"],
            "failed_step": result["failed_step"],
        },
    )


@require_POST
def create_parking_entry(request: HttpRequest) -> JsonResponse:
    payload = _decode_json_body(request)
    result = EntrySagaOrchestrationService().execute(
        vehicle_num=payload["vehicle_num"],
        slot_id=payload["slot_id"],
        requested_at=payload["requested_at"],
        idempotency_key=request.headers["Idempotency-Key"],
    )

    if result["status"] == "COMPENSATED":
        return _build_compensated_response(
            message="입차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
            result=result,
        )

    return JsonResponse(result, status=HTTPStatus.CREATED)


@require_POST
def create_parking_exit(request: HttpRequest) -> JsonResponse:
    payload = _decode_json_body(request)
    result = ExitSagaOrchestrationService().execute(
        vehicle_num=payload["vehicle_num"],
        requested_at=payload["requested_at"],
        idempotency_key=request.headers["Idempotency-Key"],
    )

    if result["status"] == "COMPENSATED":
        return _build_compensated_response(
            message="출차 SAGA 처리 중 보상 트랜잭션이 실행되었습니다.",
            result=result,
        )

    return JsonResponse(result, status=HTTPStatus.OK)


@require_GET
def get_saga_operation_status(request: HttpRequest, operation_id: str) -> JsonResponse:
    result = OperationStatusQueryService().get(operation_id=operation_id)
    return JsonResponse(result, status=HTTPStatus.OK)
