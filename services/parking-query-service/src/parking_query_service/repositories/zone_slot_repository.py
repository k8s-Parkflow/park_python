from __future__ import annotations

from typing import TypedDict

from parking_query_service.clients.grpc.zone import ZoneGrpcClient
from parking_query_service.models.current_parking_view import CurrentParkingView


class ZoneSlotRow(TypedDict):
    slot_id: int
    slot_name: str
    category: str
    is_active: bool
    vehicle_num: str | None


class ZoneExistenceRepository:
    def __init__(self, *, zone_client: ZoneGrpcClient | None = None) -> None:
        self._zone_client = zone_client or ZoneGrpcClient()

    def exists(self, *, zone_id: int) -> bool:
        return self._zone_client.exists_by_zone_id(zone_id)


class ZoneSlotRepository:
    def __init__(self, *, zone_client: ZoneGrpcClient | None = None) -> None:
        self._zone_client = zone_client or ZoneGrpcClient()

    def list_by_zone_id(self, *, zone_id: int) -> list[ZoneSlotRow]:
        slots = self._zone_client.get_zone_slots(zone_id=zone_id)
        if not slots:
            return []

        vehicle_nums_by_slot_id = self._load_vehicle_nums_by_slot_id(
            slot_ids=[slot["slot_id"] for slot in slots]
        )

        return [
            {
                **slot,
                "vehicle_num": vehicle_nums_by_slot_id.get(slot["slot_id"]),
            }
            for slot in slots
        ]

    def _load_vehicle_nums_by_slot_id(self, *, slot_ids: list[int]) -> dict[int, str]:
        rows = (
            CurrentParkingView.objects.filter(slot_id__in=slot_ids)
            .order_by("slot_id", "-entry_at", "-updated_at")
            .values("slot_id", "vehicle_num")
        )

        latest_vehicle_nums: dict[int, str] = {}
        for row in rows:
            latest_vehicle_nums.setdefault(row["slot_id"], row["vehicle_num"])

        return latest_vehicle_nums
