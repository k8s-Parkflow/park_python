import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from park_py.error_handling import ApplicationError, ErrorCode
from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ZoneAvailability
from parking_query_service.services import get_current_parking
from parking_query_service.services import project_entry
from parking_query_service.services import project_exit
from parking_query_service.services import restore_exit
from parking_query_service.services import revert_entry


def _payload(request) -> dict:
    return json.loads(request.body.decode("utf-8"))


@require_GET
def get_current_parking_view(_request, vehicle_num: str) -> JsonResponse:
    try:
        result = get_current_parking(vehicle_num=vehicle_num)
    except CurrentParkingView.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result)


@require_POST
def project_parking_entry(request) -> JsonResponse:
    payload = _payload(request)
    try:
        result = project_entry(
            vehicle_num=payload["vehicle_num"],
            slot_id=payload["slot_id"],
            zone_id=payload["zone_id"],
            slot_type=payload["slot_type"],
            entry_at=payload["entry_at"],
        )
    except ZoneAvailability.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result, status=200)


@require_POST
def revert_parking_entry_projection(request) -> JsonResponse:
    payload = _payload(request)
    result = revert_entry(vehicle_num=payload["vehicle_num"])
    return JsonResponse(result, status=200)


@require_POST
def project_parking_exit(request) -> JsonResponse:
    payload = _payload(request)
    try:
        result = project_exit(vehicle_num=payload["vehicle_num"])
    except (CurrentParkingView.DoesNotExist, ZoneAvailability.DoesNotExist) as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result, status=200)


@require_POST
def restore_parking_exit_projection(request) -> JsonResponse:
    payload = _payload(request)
    try:
        result = restore_exit(
            vehicle_num=payload["vehicle_num"],
            slot_id=payload["slot_id"],
            zone_id=payload["zone_id"],
            slot_type=payload["slot_type"],
            entry_at=payload["entry_at"],
        )
    except ZoneAvailability.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result, status=200)
