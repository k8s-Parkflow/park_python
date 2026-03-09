from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from parking_query_service.forms import CurrentLocationQueryForm
from parking_query_service.repositories.current_location_repository import CurrentLocationRepository
from parking_query_service.repositories.vehicle_repository import VehicleRepository
from parking_query_service.services.current_location_service import CurrentLocationService


@require_GET
def get_current_location(_request, vehicle_num: str) -> JsonResponse:
    form = CurrentLocationQueryForm(data={"vehicle_num": vehicle_num})
    if not form.is_valid():
        raise ValidationError(form.errors)

    service = CurrentLocationService(
        current_location_repository=CurrentLocationRepository(),
        vehicle_repository=VehicleRepository(),
    )
    return JsonResponse(service.get_current_location(form.cleaned_data["vehicle_num"]))
