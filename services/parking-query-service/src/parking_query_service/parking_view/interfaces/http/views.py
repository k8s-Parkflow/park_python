import json
from json import JSONDecodeError

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    PolymorphicProxySerializer,
    extend_schema,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response

from park_py.error_handling import ApplicationError, ErrorCode
from parking_query_service.dependencies import build_current_location_service
from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ZoneAvailability
from parking_query_service.parking_view.interfaces.http.forms import CurrentLocationQueryForm
from parking_query_service.parking_view.interfaces.http.serializers import (
    ErrorResponseSerializer,
    TotalAvailabilitySerializer,
    TypedAvailabilitySerializer,
)
from parking_query_service.services import get_current_parking
from parking_query_service.services import project_entry
from parking_query_service.services import project_exit
from parking_query_service.services import restore_exit
from parking_query_service.services import revert_entry
from parking_query_service.services.zone_availability_service import (
    ZoneAvailabilityService,
)


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


def get_current_location(_request: HttpRequest, vehicle_num: str) -> JsonResponse:
    form = CurrentLocationQueryForm(data={"vehicle_num": vehicle_num})
    if not form.is_valid():
        raise ValidationError(form.errors)

    payload = build_current_location_service().get_current_location(
        form.cleaned_data["vehicle_num"]
    )
    return JsonResponse(payload, status=200)


@require_GET
def get_current_parking_view(_request, vehicle_num: str) -> JsonResponse:
    try:
        result = get_current_parking(vehicle_num=vehicle_num)
    except CurrentParkingView.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result)


@csrf_exempt
@require_POST
def project_parking_entry(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "vehicle_num", "slot_id", "zone_id", "slot_type", "entry_at")
    try:
        result = project_entry(
            operation_id=payload["operation_id"],
            vehicle_num=payload["vehicle_num"],
            slot_id=payload["slot_id"],
            zone_id=payload["zone_id"],
            slot_type=payload["slot_type"],
            entry_at=payload["entry_at"],
        )
    except ZoneAvailability.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result, status=200)


@csrf_exempt
@require_POST
def revert_parking_entry_projection(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "vehicle_num")
    result = revert_entry(
        operation_id=payload["operation_id"],
        vehicle_num=payload["vehicle_num"],
    )
    return JsonResponse(result, status=200)


@csrf_exempt
@require_POST
def project_parking_exit(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "vehicle_num")
    try:
        result = project_exit(
            operation_id=payload["operation_id"],
            vehicle_num=payload["vehicle_num"],
        )
    except (CurrentParkingView.DoesNotExist, ZoneAvailability.DoesNotExist) as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result, status=200)


@csrf_exempt
@require_POST
def restore_parking_exit_projection(request) -> JsonResponse:
    payload = _payload(request)
    _require_fields(payload, "operation_id", "vehicle_num", "slot_id", "zone_id", "slot_type", "entry_at")
    try:
        result = restore_exit(
            operation_id=payload["operation_id"],
            vehicle_num=payload["vehicle_num"],
            slot_id=payload["slot_id"],
            zone_id=payload["zone_id"],
            slot_type=payload["slot_type"],
            entry_at=payload["entry_at"],
        )
    except ZoneAvailability.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc
    return JsonResponse(result, status=200)


@extend_schema(
    summary="전체 Zone 기준 여석 조회",
    description=(
        "slot_type를 전달하면 해당 타입의 전체 Zone 여석 총합을 반환하고, "
        "slot_type를 생략하면 전체 타입 여석 총합을 반환한다."
    ),
    parameters=[
        OpenApiParameter(
            name="slot_type",
            location=OpenApiParameter.QUERY,
            required=False,
            type=str,
            enum=["GENERAL", "EV", "DISABLED"],
            description="조회할 슬롯 타입. 대소문자 구분 없이 허용한다.",
        )
    ],
    responses={
        200: PolymorphicProxySerializer(
            component_name="ZoneAvailabilityResponse",
            serializers=[
                TypedAvailabilitySerializer,
                TotalAvailabilitySerializer,
            ],
            resource_type_field_name=None,
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="지원하지 않는 slot_type 요청",
        ),
    },
)
@api_view(["GET"])
def availability(request: HttpRequest) -> Response:
    payload = ZoneAvailabilityService().get(
        slot_type=request.GET.get("slot_type", ""),
    )
    return Response(payload)
