from django.http import JsonResponse
from django.views.decorators.http import require_GET

from park_py.error_handling import ApplicationError, ErrorCode
from parking_command_service.models import ParkingSlot
from zone_service.models.slot_type import SlotType
from zone_service.models.zone import Zone


@require_GET
def get_entry_policy(_request, slot_id: int) -> JsonResponse:
    try:
        slot = ParkingSlot.objects.get(slot_id=slot_id)
        zone = Zone.objects.get(zone_id=slot.zone_id)
        slot_type = SlotType.objects.get(slot_type_id=slot.slot_type_id)
    except (ParkingSlot.DoesNotExist, Zone.DoesNotExist, SlotType.DoesNotExist) as exc:
        raise ApplicationError(code=ErrorCode.NOT_FOUND, status=404) from exc

    return JsonResponse(
        {
            "slot_id": slot.slot_id,
            "zone_id": zone.zone_id,
            "slot_type": slot_type.type_name,
            "zone_active": True,
            "entry_allowed": slot.is_active,
        }
    )
