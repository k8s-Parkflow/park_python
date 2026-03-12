from parking_query_service.models import ZoneAvailability


class ZoneAvailabilityRepository:
    _SUPPORTED_SLOT_TYPES = ("GENERAL", "EV", "DISABLED")

    def get_counts_by_slot_type(self, *, slot_type: str) -> list[ZoneAvailability]:
        return list(self._counts_queryset(slot_type=slot_type).order_by("zone_id"))

    def _counts_queryset(self, *, slot_type: str):
        if slot_type == "":
            return ZoneAvailability.objects.filter(
                slot_type__in=self._SUPPORTED_SLOT_TYPES
            )

        return ZoneAvailability.objects.filter(slot_type=slot_type)
