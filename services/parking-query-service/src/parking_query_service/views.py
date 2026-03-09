from django.http import HttpRequest
from rest_framework.decorators import api_view
from rest_framework.response import Response

from parking_query_service.services.zone_availability_service import (
    ZoneAvailabilityService,
)


# HTTP 요청에서 타입 값을 읽고 JSON HTTP 응답을 반환한다.
@api_view(["GET"])
def availability(request: HttpRequest) -> Response:
    payload = ZoneAvailabilityService().get(
        slot_type=request.GET.get("slot_type", ""),
    )
    return Response(payload)
