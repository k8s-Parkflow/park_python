from __future__ import annotations

import time

from django.db import DatabaseError

from parking_command_service.domains.parking_record.domain import (
    ParkingHistory,
    ParkingSlot,
    SlotOccupancy,
)
from parking_query_service.models import CurrentParkingView, ZoneAvailability
from zone_service.models import SlotType


class DjangoParkingProjectionWriter:
    def record_entry(self, *, history: ParkingHistory) -> None:
        self._run_with_retry(lambda: self._record_entry(history=history))

    def record_exit(self, *, history: ParkingHistory) -> None:
        self._run_with_retry(lambda: self._record_exit(history=history))

    def _record_entry(self, *, history: ParkingHistory) -> None:
        slot_type_name = self._get_slot_type_name(slot=history.slot)
        current_view = CurrentParkingView.objects.select_for_update().filter(
            vehicle_num=history.vehicle_num
        ).first()
        if current_view is not None and self._is_newer_projection(
            current_entry_at=current_view.entry_at,
            current_history_id=current_view.history_id,
            incoming_entry_at=history.entry_at,
            incoming_history_id=history.history_id,
        ):
            return

        CurrentParkingView.objects.update_or_create(
            vehicle_num=history.vehicle_num,
            defaults={
                "history_id": history.history_id,
                "slot_id": history.slot_id,
                "zone_id": history.slot.zone_id,
                "slot_code": history.slot.slot_code,
                "slot_type": slot_type_name,
                "entry_at": history.entry_at,
            },
        )
        self._sync_zone_availability(slot=history.slot, slot_type_name=slot_type_name)

    def _record_exit(self, *, history: ParkingHistory) -> None:
        slot_type_name = self._get_slot_type_name(slot=history.slot)
        current_view = CurrentParkingView.objects.select_for_update().filter(
            vehicle_num=history.vehicle_num
        ).first()
        if current_view is not None and not self._is_newer_projection(
            current_entry_at=current_view.entry_at,
            current_history_id=current_view.history_id,
            incoming_entry_at=history.entry_at,
            incoming_history_id=history.history_id,
        ):
            current_view.delete()

        self._sync_zone_availability(slot=history.slot, slot_type_name=slot_type_name)

    def _sync_zone_availability(self, *, slot: ParkingSlot, slot_type_name: str) -> None:
        total_count = ParkingSlot.objects.filter(
            zone_id=slot.zone_id,
            slot_type_id=slot.slot_type_id,
            is_active=True,
        ).count()
        occupied_count = SlotOccupancy.objects.filter(
            slot__zone_id=slot.zone_id,
            slot__slot_type_id=slot.slot_type_id,
            slot__is_active=True,
            occupied=True,
        ).count()

        ZoneAvailability.objects.update_or_create(
            zone_id=slot.zone_id,
            slot_type=slot_type_name,
            defaults={
                "total_count": total_count,
                "occupied_count": occupied_count,
                "available_count": total_count - occupied_count,
            },
        )

    def _get_slot_type_name(self, *, slot: ParkingSlot) -> str:
        return SlotType.objects.only("type_name").get(slot_type_id=slot.slot_type_id).type_name

    def _run_with_retry(self, operation) -> None:
        for attempt in range(3):
            try:
                operation()
                return
            except DatabaseError as exc:
                # SQLite 테스트 환경의 짧은 write lock은 제한된 재시도로 흡수한다.
                if "locked" not in str(exc).lower() or attempt == 2:
                    raise
                time.sleep(0.01)

    @staticmethod
    def _is_newer_projection(
        *,
        current_entry_at,
        current_history_id: int | None,
        incoming_entry_at,
        incoming_history_id: int | None,
    ) -> bool:
        current_key = (current_entry_at, current_history_id or 0)
        incoming_key = (incoming_entry_at, incoming_history_id or 0)
        return current_key > incoming_key
