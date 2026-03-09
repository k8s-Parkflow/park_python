from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.domain import (
    ParkingHistory,
    ParkingHistoryStatus,
    ParkingSlot,
    SlotOccupancy,
)

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))


# 주차 이력 도메인 단위 테스트 클래스
class ParkingHistoryDomainTests(SimpleTestCase):
    # 차량 번호 정규화 검증
    def test_should_normalize_vehicle_num__when_history_started(self) -> None:
        # Given
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        entry_at = timezone.now()

        # When
        history = ParkingHistory.start(slot=slot, vehicle_num=" 69가-3455 ", entry_at=entry_at)

        # Then
        self.assertEqual(history.vehicle_num, "69가3455")
        self.assertEqual(history.status, ParkingHistoryStatus.PARKED)
        self.assertEqual(history.entry_at, entry_at)

    # 출차 시각 역전 거부 검증
    def test_should_reject_exit_before_entry__when_exit_called(self) -> None:
        # Given
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        entry_at = timezone.now()
        history = ParkingHistory.start(slot=slot, vehicle_num="69가3455", entry_at=entry_at)

        # When / Then
        with self.assertRaisesMessage(ValidationError, "출차 시각은 입차 시각보다 빠를 수 없습니다."):
            history.exit(exited_at=entry_at - timedelta(minutes=1))


# 슬롯 점유 도메인 단위 테스트 클래스
class SlotOccupancyDomainTests(SimpleTestCase):
    # 점유 및 해제 상태 전이 검증
    def test_should_set_and_clear_occupancy_fields__when_occupy_and_release_called(self) -> None:
        # Given
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        entry_at = timezone.now()
        history = ParkingHistory(
            history_id=101,
            slot=slot,
            vehicle_num="69가3455",
            status=ParkingHistoryStatus.PARKED,
            entry_at=entry_at,
        )
        occupancy = SlotOccupancy(slot=slot)

        # When
        occupancy.occupy(vehicle_num="69가-3455", history=history, occupied_at=entry_at)

        # Then
        self.assertTrue(occupancy.occupied)
        self.assertEqual(occupancy.vehicle_num, "69가3455")
        self.assertEqual(occupancy.history, history)
        self.assertEqual(occupancy.occupied_at, entry_at)

        # When
        occupancy.release()

        # Then
        self.assertFalse(occupancy.occupied)
        self.assertIsNone(occupancy.vehicle_num)
        self.assertIsNone(occupancy.history)
        self.assertIsNone(occupancy.occupied_at)
