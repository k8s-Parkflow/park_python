from django.http import HttpRequest, JsonResponse

from parking_query_service.services.zone_availability_service import (
    ZoneAvailabilityService,
)


def zone_availability_view(request: HttpRequest) -> JsonResponse:
    payload = ZoneAvailabilityService().get(
        slot_type=request.GET.get("slot_type", ""),
    )
    return JsonResponse(payload)
