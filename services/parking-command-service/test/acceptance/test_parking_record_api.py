from __future__ import annotations

import sys
import threading
import time
from datetime import timedelta
from pathlib import Path

from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.domain import (
    ParkingHistory,
    ParkingHistoryStatus,
    SlotOccupancy,
)

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from support.api import post_entry, post_exit
from support.factories import (
    create_empty_occupancy,
    create_occupied_session,
    create_slot,
    create_vehicle,
)


# 인수 테스트 공통 검증 보조 클래스
class ParkingRecordAcceptanceSupport(TestCase):
    maxDiff = None

    # 활성 주차 상태 검증 유틸리티
    def assert_parked(self, *, vehicle_num: str, slot_id: int) -> None:
        history = ParkingHistory.objects.get()
        occupancy = SlotOccupancy.objects.get(slot_id=slot_id)
        self.assertEqual(history.status, ParkingHistoryStatus.PARKED)
        self.assertTrue(occupancy.occupied)
        self.assertEqual(occupancy.vehicle_num, vehicle_num)
        self.assertEqual(occupancy.history_id, history.history_id)

    # 해제된 점유 상태 검증 유틸리티
    def assert_released(self, *, slot_id: int) -> None:
        occupancy = SlotOccupancy.objects.get(slot_id=slot_id)
        self.assertFalse(occupancy.occupied)
        self.assertIsNone(occupancy.vehicle_num)
        self.assertIsNone(occupancy.history_id)
        self.assertIsNone(occupancy.occupied_at)


# 입차 API 인수 테스트 클래스
class ParkingRecordEntryAcceptanceTests(ParkingRecordAcceptanceSupport):
    # 입차 성공 흐름 검증
    def test_should_create_entry__when_requested(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)
        entry_at = timezone.now()

        # When
        response = post_entry(
            self.client,
            vehicle_num="69가-3455",
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=slot.slot_id,
            entry_at=entry_at,
        )

        # Then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "history_id": ParkingHistory.objects.get().history_id,
                "vehicle_num": vehicle.vehicle_num,
                "zone_id": slot.zone_id,
                "slot_code": slot.slot_code,
                "slot_id": slot.slot_id,
                "status": "PARKED",
                "entry_at": entry_at.isoformat(),
                "exit_at": None,
            },
        )
        self.assert_parked(vehicle_num=vehicle.vehicle_num, slot_id=slot.slot_id)

    # 차량 미등록 입차 거부 검증
    def test_should_reject_entry__when_vehicle_missing(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        response = post_entry(
            self.client,
            vehicle_num="69가-3455",
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=slot.slot_id,
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertEqual(ParkingHistory.objects.count(), 0)

    # 슬롯 미존재 입차 거부 검증
    def test_should_reject_entry__when_slot_missing(self) -> None:
        # Given
        create_vehicle()

        # When
        response = post_entry(
            self.client,
            vehicle_num="69가-3455",
            zone_id=1,
            slot_code="A001",
            slot_id=9999,
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertEqual(ParkingHistory.objects.count(), 0)

    # 비활성 슬롯 입차 거부 검증
    def test_should_reject_entry__when_slot_inactive(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot(is_active=False)
        create_empty_occupancy(slot=slot)

        # When
        response = post_entry(
            self.client,
            vehicle_num=vehicle.vehicle_num,
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=slot.slot_id,
        )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "conflict")

    # 점유 중 슬롯 입차 거부 검증
    def test_should_reject_entry__when_slot_occupied(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        create_occupied_session(
            slot=slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=1),
        )
        another_vehicle = create_vehicle(vehicle_num="70가1234")

        # When
        response = post_entry(
            self.client,
            vehicle_num=another_vehicle.vehicle_num,
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=slot.slot_id,
        )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "conflict")

    # 활성 세션 중복 입차 거부 검증
    def test_should_reject_entry__when_vehicle_already_parked(self) -> None:
        # Given
        vehicle = create_vehicle()
        current_slot = create_slot(slot_code="A001")
        create_occupied_session(
            slot=current_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=2),
        )
        target_slot = create_slot(slot_code="A002")
        create_empty_occupancy(slot=target_slot)

        # When
        response = post_entry(
            self.client,
            vehicle_num=vehicle.vehicle_num,
            zone_id=target_slot.zone_id,
            slot_code=target_slot.slot_code,
            slot_id=target_slot.slot_id,
        )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "conflict")
        self.assertEqual(ParkingHistory.objects.filter(exit_at__isnull=True).count(), 1)


# 출차 API 인수 테스트 클래스
class ParkingRecordExitAcceptanceTests(ParkingRecordAcceptanceSupport):
    # 출차 성공 흐름 검증
    def test_should_complete_exit__when_requested(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now() - timedelta(hours=3)
        exit_at = timezone.now()
        history, _ = create_occupied_session(
            slot=slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=entry_at,
        )

        # When
        response = post_exit(
            self.client,
            vehicle_num="69가-3455",
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=slot.slot_id,
            exit_at=exit_at,
        )

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "history_id": history.history_id,
                "vehicle_num": vehicle.vehicle_num,
                "zone_id": slot.zone_id,
                "slot_code": slot.slot_code,
                "slot_id": slot.slot_id,
                "status": "EXITED",
                "entry_at": entry_at.isoformat(),
                "exit_at": exit_at.isoformat(),
            },
        )
        history.refresh_from_db()
        self.assertEqual(history.status, ParkingHistoryStatus.EXITED)
        self.assertEqual(history.exit_at, exit_at)
        self.assert_released(slot_id=slot.slot_id)

    # 활성 세션 미존재 출차 거부 검증
    def test_should_reject_exit__when_active_history_missing(self) -> None:
        # Given
        create_vehicle()

        # When
        response = post_exit(self.client, vehicle_num="69가-3455", zone_id=1, slot_code="A001", slot_id=1)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    # 출차 시각 역전 거부 검증
    def test_should_reject_exit__when_exit_time_is_early(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now()
        create_occupied_session(slot=slot, vehicle_num=vehicle.vehicle_num, entry_at=entry_at)

        # When
        response = post_exit(
            self.client,
            vehicle_num=vehicle.vehicle_num,
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=slot.slot_id,
            exit_at=entry_at - timedelta(minutes=1),
        )

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "bad_request")


# 요청 검증 인수 테스트 클래스
class ParkingRecordValidationAcceptanceTests(ParkingRecordAcceptanceSupport):
    # 입차 요청 검증 실패 응답 검증
    def test_should_reject_entry__when_payload_invalid(self) -> None:
        # Given
        create_vehicle()

        # When
        missing_slot_response = post_entry(self.client, vehicle_num="69가-3455")
        invalid_vehicle_response = post_entry(
            self.client,
            vehicle_num="invalid",
            zone_id=1,
            slot_code="A001",
            slot_id=1,
        )

        # Then
        self.assertEqual(missing_slot_response.status_code, 400)
        self.assertEqual(invalid_vehicle_response.status_code, 400)

    # 출차 요청 검증 실패 응답 검증
    def test_should_reject_exit__when_payload_invalid(self) -> None:
        # Given
        create_vehicle()

        # When
        response = self.client.post(
            "/api/parking/exit",
            data='{"vehicle_num":"69가-3455","zone_id":1,"slot_code":"A001","slot_id":1,"exit_at":"2026-03-09T12:10:00"}',
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 400)


# 동시 입차 인수 테스트 클래스
class ParkingRecordConcurrencyAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    # 동시 입차 경쟁 보호 검증
    def test_should_allow_one_entry__when_requests_compete(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        create_vehicle(vehicle_num="70가1234")
        responses: list[int] = []
        first_request_started = threading.Event()

        def send_entry(vehicle_num: str, *, mark_started: bool = False) -> None:
            client = Client()
            if mark_started:
                first_request_started.set()
            response = post_entry(
                client,
                vehicle_num=vehicle_num,
                zone_id=slot.zone_id,
                slot_code=slot.slot_code,
                slot_id=slot.slot_id,
            )
            responses.append(response.status_code)

        # When
        first = threading.Thread(target=send_entry, args=("69가3455",), kwargs={"mark_started": True})
        first.start()
        first_request_started.wait(timeout=1)
        time.sleep(0.01)
        second = threading.Thread(target=send_entry, args=("70가1234",))
        second.start()
        first.join()
        second.join()

        # Then
        self.assertCountEqual(responses, [201, 409])
        self.assertEqual(ParkingHistory.objects.filter(exit_at__isnull=True).count(), 1)
        self.assertEqual(SlotOccupancy.objects.filter(occupied=True).count(), 1)
    # 슬롯 식별 불일치 거부 검증
    def test_should_reject_entry__when_slot_identifiers_mismatch(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot(zone_id=1, slot_code="A001")
        create_empty_occupancy(slot=slot)
        another_slot = create_slot(zone_id=2, slot_code="B001")
        create_empty_occupancy(slot=another_slot)

        # When
        response = post_entry(
            self.client,
            vehicle_num=vehicle.vehicle_num,
            zone_id=slot.zone_id,
            slot_code=slot.slot_code,
            slot_id=another_slot.slot_id,
        )

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "bad_request")
        self.assertEqual(ParkingHistory.objects.count(), 0)

    # 출차 위치 충돌 거부 검증
    def test_should_reject_exit__when_location_conflicts(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot(zone_id=1, slot_code="A001")
        other_slot = create_slot(zone_id=1, slot_code="A002")
        create_occupied_session(
            slot=slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=1),
        )

        # When
        response = post_exit(
            self.client,
            vehicle_num=vehicle.vehicle_num,
            zone_id=other_slot.zone_id,
            slot_code=other_slot.slot_code,
            slot_id=other_slot.slot_id,
        )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "conflict")
