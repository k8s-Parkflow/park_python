from __future__ import annotations

import json
import sys
from pathlib import Path

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from parking_command_service.domains.parking_record.presentation.http.serializers import (
    parse_entry_command,
    parse_exit_command,
)

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))


# 요청 파서 단위 테스트 클래스
class ParkingRecordSerializerUnitTests(SimpleTestCase):
    # 입차 요청 차량 번호 정규화 검증
    def test_should_normalize_vehicle_num__when_entry_parsed(self) -> None:
        # Given
        body = json.dumps(
            {
                "vehicle_num": " 69가-3455 ",
                "zone_id": 1,
                "slot_name": "A001",
                "slot_id": 1,
            }
        ).encode()

        # When
        command = parse_entry_command(body=body)

        # Then
        self.assertEqual(command.vehicle_num, "69가3455")
        self.assertEqual(command.zone_id, 1)
        self.assertEqual(command.slot_name, "A001")
        self.assertEqual(command.slot_id, 1)

    # naive datetime 거부 검증
    def test_should_reject_naive_datetime__when_exit_parsed(self) -> None:
        # Given
        body = json.dumps(
            {
                "vehicle_num": "69가3455",
                "zone_id": 1,
                "slot_name": "A001",
                "slot_id": 1,
                "exit_at": "2026-03-09T12:10:00",
            }
        ).encode()

        # When / Then
        with self.assertRaises(ValidationError) as captured:
            parse_exit_command(body=body)

        self.assertEqual(
            captured.exception.message_dict,
            {"exit_at": ["timezone-aware datetime이어야 합니다."]},
        )

    # slot_name 원형 유지 검증
    def test_should_keep_slot_name__when_entry_parsed(self) -> None:
        # Given
        body = json.dumps(
            {
                "vehicle_num": "69가3455",
                "zone_id": 1,
                "slot_name": "A001",
                "slot_id": 1,
            }
        ).encode()

        # When
        command = parse_entry_command(body=body)

        # Then
        self.assertEqual(command.slot_name, "A001")

    # slot_name 공백 거부 검증
    def test_should_reject_slot_name__when_surrounded_by_spaces(self) -> None:
        # Given
        body = json.dumps(
            {
                "vehicle_num": "69가3455",
                "zone_id": 1,
                "slot_name": " A001 ",
                "slot_id": 1,
            }
        ).encode()

        # When / Then
        with self.assertRaises(ValidationError) as captured:
            parse_entry_command(body=body)

        self.assertEqual(
            captured.exception.message_dict,
            {"slot_name": ["앞뒤 공백 없이 입력해야 합니다."]},
        )

    # slot_name 소문자 거부 검증
    def test_should_reject_slot_name__when_lowercase(self) -> None:
        # Given
        body = json.dumps(
            {
                "vehicle_num": "69가3455",
                "zone_id": 1,
                "slot_name": "a001",
                "slot_id": 1,
            }
        ).encode()

        # When / Then
        with self.assertRaises(ValidationError) as captured:
            parse_entry_command(body=body)

        self.assertEqual(
            captured.exception.message_dict,
            {"slot_name": ["대문자 형식이어야 합니다."]},
        )
