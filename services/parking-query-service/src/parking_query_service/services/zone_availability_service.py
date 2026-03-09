from typing import Any, Optional

from parking_query_service.models import ZoneAvailability
from zone_service.models import Zone


class ZoneAvailabilityService:

    # 전체 Zone 기준 타입별 잔여석 총합 조회에 필요한 의존성을 받는다.
    def __init__(
        self,
        *,
        zone_repository: Optional[Any] = None,
        zone_availability_repository: Optional[Any] = None,
    ) -> None:
        self._zone_repository = zone_repository
        self._zone_availability_repository = zone_availability_repository

    # 요청한 타입 전체 Zone 잔여석 총합 응답
    def get(self, *, slot_type: str) -> dict[str, Any]:
        zone_ids = self._zone_ids()
        counts = self._counts(slot_type=slot_type)
        total = self._total_available_count(zone_ids=zone_ids, counts=counts)
        return self._build_response(slot_type=slot_type, total=total)

    # 전체 합산 대상 Zone 식별자 집합
    def _zone_ids(self) -> set[int]:
        zones = self._zones()
        return {zone.zone_id for zone in zones}

    # 전체 합산 대상 Zone 목록 조회
    def _zones(self) -> list[Any]:
        if self._zone_repository is not None:
            return self._zone_repository.list_zones()
        return list(Zone.objects.order_by("zone_id"))

    # 요청한 타입의 여석 집계 목록 조회
    def _counts(self, *, slot_type: str) -> list[Any]:
        if self._zone_availability_repository is not None:
            return self._zone_availability_repository.get_counts_by_slot_type(
                slot_type=slot_type,
            )
        return list(
            ZoneAvailability.objects.filter(slot_type=slot_type).order_by("zone_id")
        )

    # 합산 대상 Zone에 속한 여석만 더해 총합 계산
    def _total_available_count(self, *, zone_ids: set[int], counts: list[Any]) -> int:
        return sum(
            count.available_count
            for count in counts
            if count.zone_id in zone_ids
        )

    # API 응답 규격에 맞는 결과
    def _build_response(self, *, slot_type: str, total: int) -> dict[str, Any]:
        return {
            "slotType": slot_type,
            "availableCount": total,
        }
