from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.application.dtos import (
    EntryCommand,
    ExitCommand,
)
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
    ParkingSlot,
    SlotOccupancy,
)

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))


# 서비스 테스트 공통 조립 클래스
class ParkingRecordServiceTestSupport(TestCase):
    # 입차 서비스 의존성 조립 유틸리티
    def make_entry_deps(self) -> tuple[ParkingSlot, SlotOccupancy, Mock, Mock]:
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        occupancy = SlotOccupancy(slot=slot)
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        vehicle_repository.exists.return_value = True
        parking_record_repository.get_slot_for_update.return_value = slot
        parking_record_repository.get_slot_by_identity_for_update.return_value = slot
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.has_active_history_for_vehicle.return_value = False
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy
        return slot, occupancy, parking_record_repository, vehicle_repository

    # 서비스 인스턴스 생성 유틸리티
    def make_service(
        self,
        *,
        parking_record_repository: Mock,
        vehicle_repository: Mock,
    ) -> ParkingRecordCommandService:
        return ParkingRecordCommandService(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )


# 입차 서비스 단위 테스트 클래스
class ParkingRecordEntryServiceUnitTests(ParkingRecordServiceTestSupport):
    # 입차 서비스 상태 변경 검증
    def test_should_create_entry__when_service_called(self) -> None:
        # Given
        entry_at = timezone.now()
        slot, occupancy, parking_record_repository, vehicle_repository = self.make_entry_deps()

        def save_history(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = save_history
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_entry(
            command=EntryCommand(
                vehicle_num="69가3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                entry_at=entry_at,
            )
        )

        # Then
        self.assertEqual(snapshot.history_id, 101)
        self.assertEqual(snapshot.vehicle_num, "69가3455")
        self.assertEqual(snapshot.zone_id, slot.zone_id)
        self.assertEqual(snapshot.slot_code, slot.slot_code)
        self.assertEqual(snapshot.slot_id, slot.slot_id)
        self.assertEqual(snapshot.status, ParkingHistoryStatus.PARKED)
        self.assertEqual(snapshot.entry_at, entry_at)
        self.assertIsNone(snapshot.exit_at)
        self.assertTrue(occupancy.occupied)
        parking_record_repository.get_slot_by_identity_for_update.assert_called_once_with(
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
        )
        parking_record_repository.save_history.assert_called_once()
        parking_record_repository.save_occupancy.assert_called_once()

    # 슬롯 식별 불일치 거부 검증
    def test_should_reject_entry__when_slot_identifiers_mismatch(self) -> None:
        # Given
        slot, _occupancy, parking_record_repository, vehicle_repository = self.make_entry_deps()
        parking_record_repository.get_slot_by_identity_for_update.return_value = ParkingSlot(
            slot_id=2,
            zone_id=2,
            slot_type_id=1,
            slot_code="B001",
            is_active=True,
        )
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When / Then
        with self.assertRaises(ParkingRecordBadRequestError):
            service.create_entry(
                command=EntryCommand(
                    vehicle_num="69가3455",
                    zone_id=slot.zone_id,
                    slot_code=slot.slot_code,
                    slot_id=slot.slot_id,
                    entry_at=timezone.now(),
                )
            )

    # trusted gRPC 입차는 로컬 slot active 상태를 재검증하지 않음
    def test_should_allow_trusted_entry__when_slot_inactive_locally(self) -> None:
        # Given
        entry_at = timezone.now()
        slot, occupancy, parking_record_repository, vehicle_repository = self.make_entry_deps()
        slot.is_active = False

        def save_history(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = save_history
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_entry(
            command=EntryCommand(
                vehicle_num="69가3455",
                zone_id=1,
                slot_code="A001",
                slot_id=1,
                slot_type="GENERAL",
                trusted_slot_metadata=True,
                entry_at=entry_at,
            )
        )

        # Then
        self.assertEqual(snapshot.history_id, 101)
        self.assertTrue(occupancy.occupied)
        parking_record_repository.get_slot_by_identity_for_update.assert_not_called()

    # 조회 차량 번호 정규화 검증
    def test_should_normalize_vehicle_num__when_entry_queries_active_history(self) -> None:
        # Given
        slot, _occupancy, parking_record_repository, vehicle_repository = self.make_entry_deps()

        def save_history(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = save_history
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        service.create_entry(
            command=EntryCommand(
                vehicle_num="69가-3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                entry_at=timezone.now(),
            )
        )

        # Then
        vehicle_repository.exists.assert_called_once_with(vehicle_num="69가3455")
        parking_record_repository.has_active_history_for_vehicle.assert_called_once_with(
            vehicle_num="69가3455"
        )


# 출차 서비스 단위 테스트 클래스
class ParkingRecordExitServiceUnitTests(ParkingRecordServiceTestSupport):
    # 출차 서비스 상태 변경 검증
    def test_should_create_exit__when_service_called(self) -> None:
        # Given
        entry_at = timezone.now()
        exit_at = timezone.now()
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        history = ParkingHistory(
            history_id=101,
            slot=slot,
            vehicle_num="69가3455",
            status=ParkingHistoryStatus.PARKED,
            entry_at=entry_at,
        )
        occupancy = SlotOccupancy(
            slot=slot,
            occupied=True,
            vehicle_num="69가3455",
            history=history,
            occupied_at=entry_at,
        )
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        parking_record_repository.get_active_history_for_vehicle_for_update.return_value = history
        parking_record_repository.get_slot_for_update.return_value = slot
        parking_record_repository.get_slot_by_identity_for_update.return_value = slot
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.save_history.side_effect = lambda *, history: history
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_exit(
            command=ExitCommand(
                vehicle_num="69가3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                exit_at=exit_at,
            )
        )

        # Then
        self.assertEqual(snapshot.history_id, 101)
        self.assertEqual(snapshot.zone_id, slot.zone_id)
        self.assertEqual(snapshot.slot_code, slot.slot_code)
        self.assertEqual(snapshot.status, ParkingHistoryStatus.EXITED)
        self.assertEqual(snapshot.exit_at, exit_at)
        self.assertFalse(occupancy.occupied)
        self.assertIsNone(occupancy.vehicle_num)
        parking_record_repository.save_history.assert_called_once()
        parking_record_repository.save_occupancy.assert_called_once()

    # 출차 위치 충돌 거부 검증
    def test_should_raise_conflict__when_exit_location_differs(self) -> None:
        # Given
        entry_at = timezone.now()
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        history = ParkingHistory(
            history_id=101,
            slot=slot,
            vehicle_num="69가3455",
            status=ParkingHistoryStatus.PARKED,
            entry_at=entry_at,
        )
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        parking_record_repository.get_active_history_for_vehicle_for_update.return_value = history
        parking_record_repository.get_slot_for_update.return_value = ParkingSlot(
            slot_id=2,
            zone_id=1,
            slot_type_id=1,
            slot_code="A002",
            is_active=True,
        )
        parking_record_repository.get_slot_by_identity_for_update.return_value = parking_record_repository.get_slot_for_update.return_value
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When / Then
        with self.assertRaises(ParkingRecordConflictError):
            service.create_exit(
                command=ExitCommand(
                    vehicle_num="69가3455",
                    zone_id=1,
                    slot_code="A002",
                    slot_id=2,
                    exit_at=timezone.now(),
                )
            )

    # 출차 조회 차량 번호 정규화 검증
    def test_should_normalize_vehicle_num__when_exit_queries_active_history(self) -> None:
        # Given
        entry_at = timezone.now()
        exit_at = timezone.now()
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        history = ParkingHistory(
            history_id=101,
            slot=slot,
            vehicle_num="69가3455",
            status=ParkingHistoryStatus.PARKED,
            entry_at=entry_at,
        )
        occupancy = SlotOccupancy(
            slot=slot,
            occupied=True,
            vehicle_num="69가3455",
            history=history,
            occupied_at=entry_at,
        )
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        parking_record_repository.get_active_history_for_vehicle_for_update.return_value = history
        parking_record_repository.get_slot_for_update.return_value = slot
        parking_record_repository.get_slot_by_identity_for_update.return_value = slot
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.save_history.side_effect = lambda *, history: history
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        service.create_exit(
            command=ExitCommand(
                vehicle_num="69가-3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                exit_at=exit_at,
            )
        )

        # Then
        parking_record_repository.get_active_history_for_vehicle_for_update.assert_called_once_with(
            vehicle_num="69가3455"
        )


# 응답 조합 단위 테스트 클래스
class ParkingRecordResponseUnitTests(ParkingRecordServiceTestSupport):
    # write 스냅샷 응답 필드 검증
    def test_should_map_snapshot_fields__when_response_built(self) -> None:
        # Given
        entry_at = timezone.now()
        slot, _occupancy, parking_record_repository, vehicle_repository = self.make_entry_deps()

        def save_history(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = save_history
        service = self.make_service(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_entry(
            command=EntryCommand(
                vehicle_num="69가3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                entry_at=entry_at,
            )
        )

        # Then
        self.assertSetEqual(
            set(snapshot.to_dict().keys()),
            {"history_id", "vehicle_num", "zone_id", "slot_code", "slot_id", "status", "entry_at", "exit_at"},
        )


# projection 연동 서비스 단위 테스트 클래스
class ParkingRecordProjectionServiceUnitTests(ParkingRecordServiceTestSupport):
    # 입차 projection 반영 호출 검증
    def test_should_call_entry_projection__when_service_succeeds(self) -> None:
        # Given
        entry_at = timezone.now()
        slot, _occupancy, parking_record_repository, vehicle_repository = self.make_entry_deps()
        projection_writer = Mock()

        def save_history(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = save_history
        service = ParkingRecordCommandService(
            parking_record_repository=parking_record_repository,
            projection_writer=projection_writer,
            vehicle_repository=vehicle_repository,
        )

        # When
        service.create_entry(
            command=EntryCommand(
                vehicle_num="69가3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                entry_at=entry_at,
            )
        )

        # Then
        projection_writer.record_entry.assert_called_once()
        projection_writer.record_exit.assert_not_called()

    # 출차 projection 반영 호출 검증
    def test_should_call_exit_projection__when_service_succeeds(self) -> None:
        # Given
        entry_at = timezone.now()
        exit_at = timezone.now()
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        history = ParkingHistory(
            history_id=101,
            slot=slot,
            vehicle_num="69가3455",
            status=ParkingHistoryStatus.PARKED,
            entry_at=entry_at,
        )
        occupancy = SlotOccupancy(
            slot=slot,
            occupied=True,
            vehicle_num="69가3455",
            history=history,
            occupied_at=entry_at,
        )
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        projection_writer = Mock()
        parking_record_repository.get_active_history_for_vehicle_for_update.return_value = history
        parking_record_repository.get_slot_for_update.return_value = slot
        parking_record_repository.get_slot_by_identity_for_update.return_value = slot
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.save_history.side_effect = lambda *, history: history
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy
        service = ParkingRecordCommandService(
            parking_record_repository=parking_record_repository,
            projection_writer=projection_writer,
            vehicle_repository=vehicle_repository,
        )

        # When
        service.create_exit(
            command=ExitCommand(
                vehicle_num="69가3455",
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
                exit_at=exit_at,
            )
        )

        # Then
        projection_writer.record_exit.assert_called_once_with(history=history)
        projection_writer.record_entry.assert_not_called()
