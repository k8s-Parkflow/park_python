from django.http import HttpRequest, JsonResponse

from parking_query_service.services.zone_availability_service import (
    ZoneAvailabilityService,
)


# HTTP 요청에서 서비스 결과 JSON 반환
def availability(request: HttpRequest) -> JsonResponse:
    payload = ZoneAvailabilityService().get(
        slot_type=request.GET.get("slot_type", ""),
    )
    return JsonResponse(payload)
