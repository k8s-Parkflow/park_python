from typing import Any, Optional

from django.core.exceptions import ValidationError

from parking_query_service.repositories import ZoneAvailabilityRepository


class ZoneAvailabilityService:
    _SUPPORTED_SLOT_TYPES = ("GENERAL", "EV", "DISABLED")

    # query projection 기준 타입별 잔여석 총합 조회에 필요한 의존성을 받는다.
    def __init__(
        self,
        *,
        zone_availability_repository: Optional[Any] = None,
    ) -> None:
        self._zone_availability_repository = (
            zone_availability_repository or ZoneAvailabilityRepository()
        )

    # 요청한 타입 projection 잔여석 총합 응답
    def get(self, *, slot_type: str) -> dict[str, Any]:
        resolved_slot_type = self._resolved_slot_type(slot_type=slot_type)
        counts = self._available_counts(slot_type=resolved_slot_type)
        total = self._sum_available_counts(counts=counts)
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

    # 요청한 타입의 여석 집계 목록 조회
    def _available_counts(self, *, slot_type: str) -> list[Any]:
        return self._zone_availability_repository.get_counts_by_slot_type(
            slot_type=slot_type,
        )

    # projection에 반영된 여석만 더해 총합 계산
    def _sum_available_counts(self, *, counts: list[Any]) -> int:
        return sum(count.available_count for count in counts)

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
