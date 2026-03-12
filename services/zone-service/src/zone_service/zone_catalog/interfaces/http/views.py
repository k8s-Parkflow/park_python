from django.http import JsonResponse
from django.views.decorators.http import require_GET

from shared.error_handling import ApplicationError, ErrorCode
from zone_service.zone_catalog.domain.entities import ParkingSlot
from zone_service.zone_catalog.infrastructure.repositories import ParkingSlotRepository


@require_GET
def get_entry_policy(_request, slot_id: int) -> JsonResponse:
    try:
        slot = ParkingSlotRepository().get(slot_id=slot_id)
    except ParkingSlot.DoesNotExist as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(
        {
            "slot_id": slot.slot_id,
            "zone_id": slot.zone.zone_id,
            "slot_type": slot.slot_type.type_name,
            "zone_active": True,
            "entry_allowed": slot.is_active,
        }
    )
