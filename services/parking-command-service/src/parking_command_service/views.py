import json

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
    return json.loads(request.body.decode("utf-8"))


@csrf_exempt
@require_POST
def create_parking_entry(request) -> JsonResponse:
    payload = _payload(request)
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
    result = cancel_entry(
        operation_id=payload["operation_id"],
        history_id=payload["history_id"],
    )
    return JsonResponse(result, status=200)


@csrf_exempt
@require_POST
def create_parking_exit(request) -> JsonResponse:
    payload = _payload(request)
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
    try:
        result = restore_exit(
            operation_id=payload["operation_id"],
            history_id=payload["history_id"],
        )
    except ParkingHistory.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(result, status=200)
