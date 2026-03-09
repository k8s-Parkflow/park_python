import json

from django.http import HttpRequest, HttpResponse

from parking_query_service.services.zone_availability_service import (
    ZoneAvailabilityService,
)


# HTTP 요청에서 타입 값을 읽고 JSON HTTP 응답을 반환한다.
def availability(request: HttpRequest) -> HttpResponse:
    payload = ZoneAvailabilityService().get(
        slot_type=request.GET.get("slot_type", ""),
    )
    return HttpResponse(
        content=json.dumps(payload),
        content_type="application/json",
    )
