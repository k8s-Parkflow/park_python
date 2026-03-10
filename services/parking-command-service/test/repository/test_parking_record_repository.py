from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from unittest.mock import Mock

from django.db import IntegrityError, close_old_connections
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.application.dtos import EntryCommand
from parking_command_service.domains.parking_record.application.exceptions import (
    ParkingRecordBadRequestError,
    ParkingRecordConflictError,
)
from parking_command_service.domains.parking_record.application.services import (
    ParkingRecordCommandService,
)
from parking_command_service.domains.parking_record.domain import (
    ParkingHistory,
    ParkingHistoryStatus,
    SlotOccupancy,
)
from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingRecordRepository,
)

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
    # zone 내부 슬롯 코드 유니크 제약 검증
    def test_should_reject_duplicate_slot_code__when_zone_reuses_code(self) -> None:
        # Given
        create_slot(zone_id=1, slot_code="A001")

        # When / Then
        with self.assertRaises(IntegrityError):
            create_slot(zone_id=1, slot_code="A001")

    # zone 간 동일 슬롯 코드 허용 검증
    def test_should_allow_same_slot_code__when_zone_differs(self) -> None:
        # Given / When
        first_slot = create_slot(zone_id=1, slot_code="A001")
        second_slot = create_slot(zone_id=2, slot_code="A001")

        # Then
        self.assertNotEqual(first_slot.slot_id, second_slot.slot_id)

    # 차량별 활성 세션 유니크 제약 검증
    def test_should_reject_second_active_history__when_vehicle_opened(self) -> None:
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
    def test_should_reject_second_active_history__when_slot_opened(self) -> None:
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
    def test_should_reject_occupied_state__when_incomplete(self) -> None:
        # Given
        slot = create_slot()

        # When / Then
        with self.assertRaises(IntegrityError):
            SlotOccupancy.objects.create(slot=slot, occupied=True)

    # 슬롯별 점유 단건성 검증
    def test_should_reject_duplicate_occupancy__when_slot_reused(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When / Then
        with self.assertRaises(IntegrityError):
            SlotOccupancy.objects.create(slot=slot)

    # 주차 이력 단건 점유 참조 검증
    def test_should_reject_reused_history__when_occupancy_created(self) -> None:
        # Given
        vehicle = create_vehicle()
        first_slot = create_slot(slot_code="A001")
        second_slot = create_slot(slot_code="A002")
        entry_at = timezone.now()
        history = create_active_history(slot=first_slot, vehicle_num=vehicle.vehicle_num, entry_at=entry_at)
        SlotOccupancy.objects.create(
            slot=first_slot,
            occupied=True,
            vehicle_num=vehicle.vehicle_num,
            history=history,
            occupied_at=entry_at,
        )

        # When / Then
        with self.assertRaises(IntegrityError):
            SlotOccupancy.objects.create(
                slot=second_slot,
                occupied=True,
                vehicle_num=vehicle.vehicle_num,
                history=history,
                occupied_at=entry_at,
            )

    # 슬롯 식별 조회 일관성 검증
    def test_should_load_same_slot__when_slot_id_and_identity_match(self) -> None:
        # Given
        slot = create_slot(zone_id=1, slot_code="A001")
        repository = DjangoParkingRecordRepository()

        # When
        slot_by_id = repository.get_lock_anchor_for_update(slot_id=slot.slot_id)
        slot_by_identity = repository.get_lock_anchor_by_identity_for_update(
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
        )

        # Then
        self.assertIsNotNone(slot_by_id)
        self.assertIsNotNone(slot_by_identity)
        self.assertEqual(slot_by_id.slot_id, slot_by_identity.slot_id)

    # trusted gRPC 입차는 로컬 inactive lock anchor에서도 실행 가능 검증
    def test_should_allow_trusted_entry__when_slot_inactive_locally(self) -> None:
        # Given
        slot = create_slot(zone_id=1, slot_code="A001", is_active=False)
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        service = ParkingRecordCommandService(
            parking_record_repository=DjangoParkingRecordRepository(),
            vehicle_repository=Mock(exists=Mock(return_value=True)),
        )

        # When
        snapshot = service.create_trusted_entry(
            command=EntryCommand(
                vehicle_num="69가3455",
                zone_id=1,
                slot_code="A001",
                slot_id=slot.slot_id,
                slot_type="GENERAL",
                entry_at=timezone.now(),
            )
        )

        # Then
        self.assertEqual(snapshot.status, ParkingHistoryStatus.PARKED)
        self.assertEqual(ParkingHistory.objects.get().slot_id, slot.slot_id)
        self.assertTrue(SlotOccupancy.objects.get(slot=slot).occupied)

    # trusted gRPC 입차는 로컬 lock anchor metadata와 무관하게 command snapshot을 저장
    def test_should_persist_trusted_snapshot__when_local_slot_metadata_differs(self) -> None:
        # Given
        slot = create_slot(zone_id=9, slot_type_id=2, slot_code="B999", is_active=False)
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        service = ParkingRecordCommandService(
            parking_record_repository=DjangoParkingRecordRepository(),
            vehicle_repository=Mock(exists=Mock(return_value=True)),
        )

        # When
        snapshot = service.create_trusted_entry(
            command=EntryCommand(
                vehicle_num="69가3455",
                zone_id=1,
                slot_code="A001",
                slot_id=slot.slot_id,
                slot_type="GENERAL",
                entry_at=timezone.now(),
            )
        )

        # Then
        history = ParkingHistory.objects.get(history_id=snapshot.history_id)
        self.assertEqual(history.slot_id, slot.slot_id)
        self.assertEqual(history.zone_id, 1)
        self.assertEqual(history.slot_type_id, 1)
        self.assertEqual(history.slot_code, "A001")
        self.assertTrue(SlotOccupancy.objects.get(slot=slot).occupied)

    # trusted gRPC 입차는 zone snapshot slot_type 없이 실행하지 않음
    def test_should_reject_trusted_entry__when_zone_slot_type_missing(self) -> None:
        # Given
        slot = create_slot(zone_id=1, slot_code="A001", is_active=False)
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        service = ParkingRecordCommandService(
            parking_record_repository=DjangoParkingRecordRepository(),
            vehicle_repository=Mock(exists=Mock(return_value=True)),
        )

        # When / Then
        with self.assertRaises(ParkingRecordBadRequestError):
            service.create_trusted_entry(
                command=EntryCommand(
                    vehicle_num="69가3455",
                    zone_id=1,
                    slot_code="A001",
                    slot_id=slot.slot_id,
                    entry_at=timezone.now(),
                )
            )
        self.assertFalse(SlotOccupancy.objects.get(slot=slot).occupied)


# 저장소 동시성 테스트 클래스
class ParkingRecordRepositoryConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    # 동시 입차 저장 일관성 검증
    def test_should_keep_consistency__when_entry_competes(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        create_vehicle(vehicle_num="70가1234")
        outcomes: list[str] = []
        outcomes_lock = threading.Lock()
        first_request_started = threading.Event()

        def run_entry(vehicle_num: str, *, mark_started: bool = False) -> None:
            close_old_connections()
            service = ParkingRecordCommandService(
                vehicle_repository=Mock(exists=Mock(return_value=True))
            )
            try:
                if mark_started:
                    first_request_started.set()
                service.create_entry(
                    command=EntryCommand(
                        vehicle_num=vehicle_num,
                        zone_id=slot.zone_id,
                        slot_code=slot.slot_code,
                        slot_id=slot.slot_id,
                        entry_at=timezone.now(),
                    )
                )
                result = "success"
            except ParkingRecordConflictError:
                result = "conflict"
            finally:
                close_old_connections()

            with outcomes_lock:
                outcomes.append(result)

        # When
        first = threading.Thread(target=run_entry, args=("69가3455",), kwargs={"mark_started": True})
        first.start()
        first_request_started.wait(timeout=1)
        time.sleep(0.01)
        second = threading.Thread(target=run_entry, args=("70가1234",))
        second.start()
        first.join()
        second.join()

        # Then
        self.assertCountEqual(outcomes, ["success", "conflict"])
        self.assertEqual(ParkingHistory.objects.filter(exit_at__isnull=True).count(), 1)
        self.assertEqual(SlotOccupancy.objects.filter(occupied=True).count(), 1)
