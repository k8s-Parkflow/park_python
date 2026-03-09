from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

from django.db import IntegrityError, close_old_connections
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from parking_command_service.dtos import EntryCommand
from parking_command_service.exceptions import ParkingRecordConflictError
from parking_command_service.models import ParkingHistory, SlotOccupancy
from parking_command_service.models.enums import ParkingHistoryStatus
from parking_command_service.services import ParkingRecordCommandService

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from support.factories import (  # noqa: E402
    create_active_history,
    create_empty_occupancy,
    create_slot,
    create_vehicle,
)


# 저장소 및 제약 테스트 클래스
class ParkingRecordRepositoryTests(TestCase):
    # 차량별 활성 세션 유니크 제약 검증
    def test_should_fail_second_active_history__when_same_vehicle_has_open_session(self) -> None:
        # Given
        vehicle = create_vehicle()
        first_slot = create_slot(slot_code="A001")
        second_slot = create_slot(slot_code="A002")
        entry_at = timezone.now()
        create_active_history(slot=first_slot, vehicle_num=vehicle.vehicle_num, entry_at=entry_at)

        # When / Then
        with self.assertRaises(IntegrityError):
            ParkingHistory.objects.create(
                slot=second_slot,
                vehicle_num=vehicle.vehicle_num,
                status=ParkingHistoryStatus.PARKED,
                entry_at=entry_at,
            )

    # 슬롯별 활성 세션 유니크 제약 검증
    def test_should_fail_second_active_history__when_same_slot_has_open_session(self) -> None:
        # Given
        first_vehicle = create_vehicle(vehicle_num="69가3455")
        second_vehicle = create_vehicle(vehicle_num="70가1234")
        slot = create_slot()
        entry_at = timezone.now()
        create_active_history(slot=slot, vehicle_num=first_vehicle.vehicle_num, entry_at=entry_at)

        # When / Then
        with self.assertRaises(IntegrityError):
            ParkingHistory.objects.create(
                slot=slot,
                vehicle_num=second_vehicle.vehicle_num,
                status=ParkingHistoryStatus.PARKED,
                entry_at=entry_at,
            )

    # 점유 상태 체크 제약 검증
    def test_should_fail__when_occupied_state_incomplete(self) -> None:
        # Given
        slot = create_slot()

        # When / Then
        with self.assertRaises(IntegrityError):
            SlotOccupancy.objects.create(slot=slot, occupied=True)

    # 슬롯별 점유 단건성 검증
    def test_should_fail_duplicate_occupancy__when_same_slot_saved_twice(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When / Then
        with self.assertRaises(IntegrityError):
            SlotOccupancy.objects.create(slot=slot)


# 저장소 동시성 테스트 클래스
class ParkingRecordRepositoryConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    # 동시 입차 저장 일관성 검증
    def test_should_keep_consistency__when_concurrent_entry_committed(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        create_vehicle(vehicle_num="70가1234")
        outcomes: list[str] = []
        outcomes_lock = threading.Lock()
        first_request_started = threading.Event()

        def request_entry(vehicle_num: str, *, mark_started: bool = False) -> None:
            close_old_connections()
            service = ParkingRecordCommandService()
            try:
                if mark_started:
                    first_request_started.set()
                service.create_entry(
                    command=EntryCommand(vehicle_num=vehicle_num, slot_id=slot.slot_id, entry_at=timezone.now())
                )
                result = "success"
            except ParkingRecordConflictError:
                result = "conflict"
            finally:
                close_old_connections()

            with outcomes_lock:
                outcomes.append(result)

        # When
        first = threading.Thread(target=request_entry, args=("69가3455",), kwargs={"mark_started": True})
        first.start()
        first_request_started.wait(timeout=1)
        time.sleep(0.01)
        second = threading.Thread(target=request_entry, args=("70가1234",))
        second.start()
        first.join()
        second.join()

        # Then
        self.assertCountEqual(outcomes, ["success", "conflict"])
        self.assertEqual(ParkingHistory.objects.filter(exit_at__isnull=True).count(), 1)
        self.assertEqual(SlotOccupancy.objects.filter(occupied=True).count(), 1)
