from __future__ import annotations

from http import HTTPStatus
from typing import Protocol, TypedDict

from park_py.error_handling import ApplicationError, ErrorCode
from parking_query_service.repositories import (
    ZoneExistenceRepository,
    ZoneSlotRepository,
    ZoneSlotRow,
)


class ZoneSlotItem(TypedDict):
    slotId: int
    slot_name: str
    category: str
    isActive: bool
    vehicleNum: str | None


class ZoneSlotPayload(TypedDict):
    zoneId: int
    slots: list[ZoneSlotItem]


class ZoneSlotRepositoryProtocol(Protocol):
    def list_by_zone_id(self, *, zone_id: int) -> list[ZoneSlotRow]:
        ...


class ZoneExistenceProtocol(Protocol):
    def exists(self, *, zone_id: int) -> bool:
        ...


class ZoneNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            "존을 찾을 수 없습니다.",
            code=ErrorCode.NOT_FOUND,
            status=HTTPStatus.NOT_FOUND,
        )


class ZoneSlotQueryService:
    def __init__(
        self,
        *,
        zone_slot_repository: ZoneSlotRepositoryProtocol | None = None,
        zone_existence: ZoneExistenceProtocol | None = None,
    ) -> None:
        self._zone_slot_repository = zone_slot_repository or ZoneSlotRepository()
        self._zone_existence = zone_existence or ZoneExistenceRepository()

    def get_zone_slots(self, *, zone_id: int) -> ZoneSlotPayload:
        if not self._zone_existence.exists(zone_id=zone_id):
            raise ZoneNotFoundError()

        return {
            "zoneId": zone_id,
            "slots": self._build_slots(zone_id=zone_id),
        }

    def _build_slots(self, *, zone_id: int) -> list[ZoneSlotItem]:
        return [
            self._build_slot_item(row=row)
            for row in self._zone_slot_repository.list_by_zone_id(zone_id=zone_id)
        ]

    @staticmethod
    def _build_slot_item(*, row: ZoneSlotRow) -> ZoneSlotItem:
        return {
            "slotId": row["slot_id"],
            "slot_name": row["slot_name"],
            "category": row["category"],
            "isActive": row["is_active"],
            "vehicleNum": row["vehicle_num"],
        }
