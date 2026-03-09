from django.http import HttpRequest
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    PolymorphicProxySerializer,
    extend_schema,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response

from parking_query_service.serializers import (
    ErrorResponseSerializer,
    TotalAvailabilitySerializer,
    TypedAvailabilitySerializer,
)
from parking_query_service.services.zone_availability_service import (
    ZoneAvailabilityService,
)


# HTTP 요청에서 타입 값을 읽고 JSON HTTP 응답을 반환한다.
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
