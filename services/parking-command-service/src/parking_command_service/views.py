import json
from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from park_py.error_handling import ApplicationError, ErrorCode
from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingSlot
from parking_command_service.services import cancel_entry
from parking_command_service.services import enter_parking
from parking_command_service.services import exit_parking
from parking_command_service.services import restore_exit


def _payload(request) -> dict:
    try:
        payload = json.loads(request.body or b"{}")
    except JSONDecodeError as exc:
        raise ValidationError({"body": ["JSON 본문 형식이 올바르지 않습니다."]}) from exc
    if not isinstance(payload, dict):
        raise ValidationError({"body": ["JSON 객체만 허용됩니다."]})
    return payload


def _require_fields(payload: dict, *required_fields: str) -> None:
    errors = {field: ["필수 입력값입니다."] for field in required_fields if field not in payload}
    if errors:
        raise ValidationError(errors)


@csrf_exempt
@require_POST
def create_parking_entry(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "vehicle_num", "slot_id", "requested_at")
    try:
        result = enter_parking(
            operation_id=payload["operation_id"],
            vehicle_num=payload["vehicle_num"],
            slot_id=payload["slot_id"],
            requested_at=payload["requested_at"],
        )
    except ParkingSlot.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(result, status=201)


@csrf_exempt
@require_POST
def cancel_parking_entry(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "history_id")
    result = cancel_entry(
        operation_id=payload["operation_id"],
        history_id=payload["history_id"],
    )
    return JsonResponse(result, status=200)


@csrf_exempt
@require_POST
def create_parking_exit(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "vehicle_num", "requested_at")
    try:
        result = exit_parking(
            operation_id=payload["operation_id"],
            vehicle_num=payload["vehicle_num"],
            requested_at=payload["requested_at"],
        )
    except ParkingHistory.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(result, status=200)


@csrf_exempt
@require_POST
def restore_parking_exit(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "history_id")
    try:
        result = restore_exit(
            operation_id=payload["operation_id"],
            history_id=payload["history_id"],
        )
    except ParkingHistory.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(result, status=200)
