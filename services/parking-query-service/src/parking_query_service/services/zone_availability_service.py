from typing import Any, Optional

from django.core.exceptions import ValidationError

from parking_query_service.repositories import ZoneAvailabilityRepository
from zone_service.models import Zone


class ZoneAvailabilityService:
    _SUPPORTED_SLOT_TYPES = ("GENERAL", "EV", "DISABLED")

    # 전체 Zone 기준 타입별 잔여석 총합 조회에 필요한 의존성을 받는다.
    def __init__(
        self,
        *,
        zone_repository: Optional[Any] = None,
        zone_availability_repository: Optional[Any] = None,
    ) -> None:
        self._zone_repository = zone_repository
        self._zone_availability_repository = (
            zone_availability_repository or ZoneAvailabilityRepository()
        )

    # 요청한 타입 전체 Zone 잔여석 총합 응답
    def get(self, *, slot_type: str) -> dict[str, Any]:
        resolved_slot_type = self._resolved_slot_type(slot_type=slot_type)
        zone_ids = self._registered_zone_ids()
        counts = self._available_counts(slot_type=resolved_slot_type)
        total = self._sum_available_counts(zone_ids=zone_ids, counts=counts)
        return self._build_response(slot_type=resolved_slot_type, total=total)

    # 입력 슬롯 타입을 표준값으로 정리하고 검증까지 마친다.
    def _resolved_slot_type(self, *, slot_type: str) -> str:
        normalized_slot_type = self._normalize_slot_type(slot_type=slot_type)
        self._validate_slot_type(slot_type=normalized_slot_type)
        return normalized_slot_type

    # 지원 타입 입력은 표준 대문자 값으로 정규화한다.
    def _normalize_slot_type(self, *, slot_type: str) -> str:
        if self._is_total_request(slot_type=slot_type):
            return ""

        return slot_type.upper()

    # slot_type이 비어 있으면 전체 조회, 그 외에는 에러 처리
    def _validate_slot_type(self, *, slot_type: str) -> None:
        if self._is_total_request(slot_type=slot_type) or self._is_supported_slot_type(
            slot_type=slot_type
        ):
            return

        raise ValidationError(
            {
                "slot_type": ["지원하지 않는 슬롯 타입입니다."],
            }
        )

    # slot_type이 없으면 전체 타입 합산 조회.
    def _is_total_request(self, *, slot_type: str) -> bool:
        return slot_type == ""

    # 지원하는 슬롯 타입인지 확인한다.
    def _is_supported_slot_type(self, *, slot_type: str) -> bool:
        return slot_type in self._SUPPORTED_SLOT_TYPES

    # 전체 합산 대상 Zone 식별자 집합
    def _registered_zone_ids(self) -> set[int]:
        zones = self._list_zones()
        return {zone.zone_id for zone in zones}

    # 전체 합산 대상 Zone 목록 조회
    def _list_zones(self) -> list[Any]:
        if self._zone_repository is not None:
            return self._zone_repository.list_zones()
        return list(Zone.objects.order_by("zone_id"))

    # 요청한 타입의 여석 집계 목록 조회
    def _available_counts(self, *, slot_type: str) -> list[Any]:
        return self._zone_availability_repository.get_counts_by_slot_type(
            slot_type=slot_type,
        )

    # 합산 대상 Zone에 속한 여석만 더해 총합 계산
    def _sum_available_counts(self, *, zone_ids: set[int], counts: list[Any]) -> int:
        return sum(
            count.available_count
            for count in counts
            if count.zone_id in zone_ids
        )

    # API 응답 규격에 맞는 결과
    def _build_response(self, *, slot_type: str, total: int) -> dict[str, Any]:
        if self._is_total_request(slot_type=slot_type):
            return {
                "availableCount": total,
            }

        return {
            "slotType": slot_type,
            "availableCount": total,
        }
