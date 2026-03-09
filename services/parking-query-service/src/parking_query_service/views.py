from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from parking_query_service.dependencies import build_current_location_service
from parking_query_service.forms import CurrentLocationQueryForm


@require_GET
def get_current_location(_request, vehicle_num: str) -> JsonResponse:
    form = CurrentLocationQueryForm(data={"vehicle_num": vehicle_num})
    if not form.is_valid():
        raise ValidationError(form.errors)

    service = build_current_location_service()
    return JsonResponse(service.get_current_location(form.cleaned_data["vehicle_num"]))
