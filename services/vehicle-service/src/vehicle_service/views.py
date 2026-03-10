from django.http import JsonResponse
from django.views.decorators.http import require_GET

from park_py.error_handling import ApplicationError, ErrorCode
from vehicle_service.models.vehicle import Vehicle


@require_GET
def get_vehicle(_request, vehicle_num: str) -> JsonResponse:
    try:
        vehicle = Vehicle.objects.get(vehicle_num=vehicle_num)
    except Vehicle.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(
        {
            "vehicle_num": vehicle.vehicle_num,
            "vehicle_type": vehicle.vehicle_type,
        }
    )

