from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingProjectionWriter,
)
from parking_query_service.models import CurrentParkingView, ZoneAvailability

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from support.factories import (  # noqa: E402
    create_active_history,
    create_occupied_session,
    create_slot,
    create_vehicle,
)


# projection 저장소 테스트 클래스
class ParkingRecordProjectionRepositoryTests(TestCase):
    # 입차 projection 생성 및 가용 현황 동기화 검증
    def test_should_record_entry_projection__when_entry_saved(self) -> None:
        # Given
        vehicle = create_vehicle()
        target_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A002")
        history, _occupancy = create_occupied_session(
            slot=target_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now(),
        )
        projection_writer = DjangoParkingProjectionWriter()

        # When
        projection_writer.record_entry(history=history)

        # Then
        current_view = CurrentParkingView.objects.get(vehicle_num=vehicle.vehicle_num)
        zone_availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")
        self.assertEqual(current_view.history_id, history.history_id)
        self.assertEqual(current_view.slot_id, target_slot.slot_id)
        self.assertEqual(current_view.zone_id, 1)
        self.assertEqual(current_view.slot_code, target_slot.slot_code)
        self.assertEqual(current_view.slot_type, "GENERAL")
        self.assertEqual(zone_availability.total_count, 2)
        self.assertEqual(zone_availability.occupied_count, 1)
        self.assertEqual(zone_availability.available_count, 1)

    # 출차 projection 제거 및 가용 현황 재계산 검증
    def test_should_record_exit_projection__when_exit_saved(self) -> None:
        # Given
        vehicle = create_vehicle()
        target_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A002")
        history, _occupancy = create_occupied_session(
            slot=target_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=1),
        )
        projection_writer = DjangoParkingProjectionWriter()
        projection_writer.record_entry(history=history)
        history.exit(exited_at=timezone.now())
        history.save(update_fields=["status", "exit_at"])
        target_slot.occupancy.release()
        target_slot.occupancy.save(update_fields=["occupied", "vehicle_num", "history", "occupied_at", "updated_at"])

        # When
        projection_writer.record_exit(history=history)

        # Then
        self.assertFalse(CurrentParkingView.objects.filter(vehicle_num=vehicle.vehicle_num).exists())
        zone_availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")
        self.assertEqual(zone_availability.total_count, 2)
        self.assertEqual(zone_availability.occupied_count, 0)
        self.assertEqual(zone_availability.available_count, 2)

    # 최신 projection 유지 회귀 검증
    def test_should_keep_newer_projection__when_older_history_arrives_late(self) -> None:
        # Given
        vehicle = create_vehicle()
        older_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        newer_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A002")
        older_history = create_active_history(
            slot=older_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=2),
        )
        CurrentParkingView.objects.create(
            vehicle_num=vehicle.vehicle_num,
            history_id=999,
            slot_id=newer_slot.slot_id,
            zone_id=newer_slot.zone_id,
            slot_code=newer_slot.slot_code,
            slot_type="GENERAL",
            entry_at=timezone.now() - timedelta(hours=1),
        )
        projection_writer = DjangoParkingProjectionWriter()

        # When
        projection_writer.record_entry(history=older_history)
        projection_writer.record_exit(history=older_history)

        # Then
        current_view = CurrentParkingView.objects.get(vehicle_num=vehicle.vehicle_num)
        self.assertEqual(current_view.slot_id, newer_slot.slot_id)
        self.assertEqual(current_view.slot_code, newer_slot.slot_code)

    # 동일 입차 시각에서는 더 큰 history_id를 유지하는 projection 회귀 검증
    def test_should_keep_higher_history_id__when_entry_time_ties(self) -> None:
        # Given
        vehicle = create_vehicle()
        first_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        second_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A002")
        tied_entry_at = timezone.now() - timedelta(hours=1)
        older_history = create_active_history(
            slot=first_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=tied_entry_at,
        )
        CurrentParkingView.objects.create(
            vehicle_num=vehicle.vehicle_num,
            history_id=older_history.history_id + 1,
            slot_id=second_slot.slot_id,
            zone_id=second_slot.zone_id,
            slot_code=second_slot.slot_code,
            slot_type="GENERAL",
            entry_at=tied_entry_at,
        )
        projection_writer = DjangoParkingProjectionWriter()

        # When
        projection_writer.record_entry(history=older_history)
        projection_writer.record_exit(history=older_history)

        # Then
        current_view = CurrentParkingView.objects.get(vehicle_num=vehicle.vehicle_num)
        self.assertEqual(current_view.history_id, older_history.history_id + 1)
        self.assertEqual(current_view.slot_id, second_slot.slot_id)
        self.assertEqual(current_view.slot_code, second_slot.slot_code)

    # 비활성 슬롯 제외 가용 집계 검증
    def test_should_exclude_inactive_slots__when_syncing_availability(self) -> None:
        # Given
        vehicle = create_vehicle()
        active_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        create_slot(
            zone_id=1,
            slot_type_id=1,
            slot_type_name="GENERAL",
            slot_code="A099",
            is_active=False,
        )
        history, _occupancy = create_occupied_session(
            slot=active_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now(),
        )
        projection_writer = DjangoParkingProjectionWriter()

        # When
        projection_writer.record_entry(history=history)

        # Then
        zone_availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")
        self.assertEqual(zone_availability.total_count, 1)
        self.assertEqual(zone_availability.occupied_count, 1)
        self.assertEqual(zone_availability.available_count, 0)
