from typing import Any

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


class ZoneAvailabilityService:
    # import 단계가 아니라 요구사항 불일치로 RED가 보이도록 최소 서비스만 둔다.
    def __init__(
        self,
        *,
        zone_repository: Any = None,
        zone_availability_repository: Any = None,
    ) -> None:
        self._zone_repository = zone_repository
        self._zone_availability_repository = zone_availability_repository

    def get(self, *, slot_type: str) -> dict[str, Any]:
        zones = self._list_zones()
        counts = self._get_counts(slot_type=slot_type)
        counts_by_zone_id = {
            count.zone_id: count.available_count
            for count in counts
        }

        # 의도적으로 구 구조를 유지해 현재 테스트가 RED로 남게 둔다.
        return {
            "criteria": {
                "slotType": slot_type,
            },
            "summary": {
                "totalAvailableCount": sum(
                    counts_by_zone_id.get(zone.zone_id, 0)
                    for zone in zones
                ),
            },
            "zones": [
                {
                    "zoneId": zone.zone_id,
                    "zoneName": zone.zone_name,
                    "availableCount": counts_by_zone_id.get(zone.zone_id, 0),
                }
                for zone in zones
            ],
        }

    def _list_zones(self) -> list[Any]:
        if self._zone_repository is not None:
            return self._zone_repository.list_zones()
        return list(Zone.objects.order_by("zone_id"))

    def _get_counts(self, *, slot_type: str) -> list[Any]:
        if self._zone_availability_repository is not None:
            return self._zone_availability_repository.get_counts_by_slot_type(
                slot_type=slot_type,
            )
        return list(ZoneAvailability.objects.filter(slot_type=slot_type).order_by("zone_id"))
