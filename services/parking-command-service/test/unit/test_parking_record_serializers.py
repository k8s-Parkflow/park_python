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
    def test_should_normalize_vehicle_num__when_entry_payload_formatted(self) -> None:
        # Given
        body = json.dumps({"vehicle_num": " 69가-3455 ", "slot_id": 1}).encode()

        # When
        command = parse_entry_command(body=body)

        # Then
        self.assertEqual(command.vehicle_num, "69가3455")
        self.assertEqual(command.slot_id, 1)

    # naive datetime 거부 검증
    def test_should_reject_naive_datetime__when_command_time_given(self) -> None:
        # Given
        body = json.dumps({"vehicle_num": "69가3455", "exit_at": "2026-03-09T12:10:00"}).encode()

        # When / Then
        with self.assertRaises(ValidationError) as captured:
            parse_exit_command(body=body)

        self.assertEqual(
            captured.exception.message_dict,
            {"exit_at": ["timezone-aware datetime이어야 합니다."]},
        )
