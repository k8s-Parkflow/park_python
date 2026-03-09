from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

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


# 성공 응답 계약 테스트 클래스
class ParkingRecordSuccessContractTests(TestCase):
    maxDiff = None

    # 입차 성공 응답 스키마 계약 검증
    def test_should_match_entry_schema__when_entry_created(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        response = post_entry(self.client, vehicle_num="69가-3455", slot_id=slot.slot_id)

        # Then
        body = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertSetEqual(
            set(body.keys()),
            {"history_id", "vehicle_num", "slot_id", "status", "entry_at", "exit_at"},
        )
        self.assertIsInstance(body["history_id"], int)
        self.assertEqual(body["vehicle_num"], vehicle.vehicle_num)
        self.assertEqual(body["slot_id"], slot.slot_id)
        self.assertEqual(body["status"], "PARKED")
        self.assertIsInstance(body["entry_at"], str)
        self.assertIsNone(body["exit_at"])

    # 출차 성공 응답 스키마 계약 검증
    def test_should_match_exit_schema__when_exit_completed(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now() - timedelta(hours=1)
        history, _ = create_occupied_session(
            slot=slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=entry_at,
        )

        # When
        response = post_exit(self.client, vehicle_num=vehicle.vehicle_num)

        # Then
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertSetEqual(
            set(body.keys()),
            {"history_id", "vehicle_num", "slot_id", "status", "entry_at", "exit_at"},
        )
        self.assertEqual(body["history_id"], history.history_id)
        self.assertEqual(body["vehicle_num"], vehicle.vehicle_num)
        self.assertEqual(body["slot_id"], slot.slot_id)
        self.assertEqual(body["status"], "EXITED")
        self.assertIsInstance(body["entry_at"], str)
        self.assertIsInstance(body["exit_at"], str)

    # write 전용 응답 필드 계약 검증
    def test_should_expose_write_fields_only__when_command_succeeds(self) -> None:
        # Given
        create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        response = post_entry(self.client, vehicle_num="69가-3455", slot_id=slot.slot_id)

        # Then
        body = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("zone_name", body)
        self.assertNotIn("slot_name", body)
        self.assertNotIn("available_count", body)


# 오류 응답 계약 테스트 클래스
class ParkingRecordErrorContractTests(TestCase):
    maxDiff = None

    # malformed JSON 응답 계약 검증
    def test_should_preserve_bad_request__when_json_malformed(self) -> None:
        # Given / When
        response = self.client.post(
            "/api/parking/entry",
            data='{"vehicle_num":"69가3455"',
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"body": ["JSON 본문 형식이 올바르지 않습니다."]},
                }
            },
        )

    # JSON 객체 외 본문 응답 계약 검증
    def test_should_preserve_bad_request__when_json_body_not_object(self) -> None:
        # Given / When
        response = self.client.post(
            "/api/parking/entry",
            data='["69가3455", 1]',
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"body": ["JSON 객체만 허용됩니다."]},
                }
            },
        )

    # slot_id 타입 오류 응답 계약 검증
    def test_should_preserve_bad_request__when_slot_id_not_integer(self) -> None:
        # Given
        create_vehicle()

        # When
        response = post_entry(self.client, vehicle_num="69가3455", slot_id="1")  # type: ignore[arg-type]

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {"slot_id": ["정수여야 합니다."]},
                }
            },
        )

    # 잘못된 요청 응답 계약 검증
    def test_should_preserve_bad_request__when_command_schema_invalid(self) -> None:
        # Given
        create_vehicle()

        # When
        response = post_entry(self.client, vehicle_num="invalid")

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": {
                        "vehicle_num": ["지원하지 않는 차량 번호 형식입니다."],
                        "slot_id": ["필수 입력값입니다."],
                    },
                }
            },
        )

    # 미존재 자원 응답 계약 검증
    def test_should_preserve_not_found__when_resource_missing(self) -> None:
        # Given
        create_vehicle()

        # When
        response = post_entry(self.client, vehicle_num="69가3455", slot_id=9999)

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "not_found",
                    "message": "존재하지 않는 슬롯입니다.",
                }
            },
        )

    # 충돌 응답 계약 검증
    def test_should_preserve_conflict__when_entry_precondition_invalid(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot(is_active=False)
        create_empty_occupancy(slot=slot)

        # When
        response = post_entry(self.client, vehicle_num=vehicle.vehicle_num, slot_id=slot.slot_id)

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "conflict",
                    "message": "비활성화된 슬롯입니다.",
                }
            },
        )

    # 출차 시각 역전 오류 계약 검증
    def test_should_preserve_error_contract__when_exit_time_invalid(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now()
        create_occupied_session(slot=slot, vehicle_num=vehicle.vehicle_num, entry_at=entry_at)

        # When
        response = post_exit(
            self.client,
            vehicle_num=vehicle.vehicle_num,
            exit_at=entry_at - timedelta(minutes=1),
        )

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            {
                "error": {
                    "code": "bad_request",
                    "message": "잘못된 요청입니다.",
                    "details": ["출차 시각은 입차 시각보다 빠를 수 없습니다."],
                }
            },
        )
