from parking_query_service.models import ZoneAvailability


class ZoneAvailabilityRepository:
    _SUPPORTED_SLOT_TYPES = ("GENERAL", "EV", "DISABLED")

    # slot_type 조건에 맞는 ZoneAvailability 집계 목록을 조회한다.
    def get_counts_by_slot_type(self, *, slot_type: str) -> list[ZoneAvailability]:
        return list(self._queryset(slot_type=slot_type).order_by("zone_id"))

    # 빈 slot_type이면 전체 지원 타입을, 아니면 요청 타입 하나만 조회한다.
    def _queryset(self, *, slot_type: str):
        if slot_type == "":
            return ZoneAvailability.objects.filter(
                slot_type__in=self._SUPPORTED_SLOT_TYPES
            )

        return ZoneAvailability.objects.filter(slot_type=slot_type)
