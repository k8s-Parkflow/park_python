from typing import Any

from django.core.exceptions import ValidationError

from parking_query_service.parking_view.domain.ports import (
    ZoneAvailabilityRepositoryProtocol,
)


class ZoneAvailabilityService:
    _SUPPORTED_SLOT_TYPES = ("GENERAL", "EV", "DISABLED")

    def __init__(
        self,
        *,
        zone_availability_repository: ZoneAvailabilityRepositoryProtocol,
    ) -> None:
        self._zone_availability_repository = zone_availability_repository

    def get(self, *, slot_type: str) -> dict[str, Any]:
        resolved_slot_type = self._resolved_slot_type(slot_type=slot_type)
        counts = self._available_counts(slot_type=resolved_slot_type)
        total = self._sum_available_counts(counts=counts)
        return self._build_response(slot_type=resolved_slot_type, total=total)

    def _resolved_slot_type(self, *, slot_type: str) -> str:
        normalized_slot_type = self._normalize_slot_type(slot_type=slot_type)
        self._validate_slot_type(slot_type=normalized_slot_type)
        return normalized_slot_type

    def _normalize_slot_type(self, *, slot_type: str) -> str:
        if self._is_total_request(slot_type=slot_type):
            return ""

        return slot_type.upper()

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

    def _is_total_request(self, *, slot_type: str) -> bool:
        return slot_type == ""

    def _is_supported_slot_type(self, *, slot_type: str) -> bool:
        return slot_type in self._SUPPORTED_SLOT_TYPES

    def _available_counts(self, *, slot_type: str) -> list[Any]:
        return self._zone_availability_repository.get_counts_by_slot_type(
            slot_type=slot_type,
        )

    def _sum_available_counts(self, *, counts: list[Any]) -> int:
        return sum(count.available_count for count in counts)

    def _build_response(self, *, slot_type: str, total: int) -> dict[str, Any]:
        if self._is_total_request(slot_type=slot_type):
            return {
                "availableCount": total,
            }

        return {
            "slotType": slot_type,
            "availableCount": total,
        }
