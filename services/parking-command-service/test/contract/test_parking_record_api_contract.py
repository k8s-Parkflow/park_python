from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

from parking_command_service.models import ParkingHistory, SlotOccupancy

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from support.factories import (  # noqa: E402
    create_active_history,
    create_empty_occupancy,
    create_slot,
    create_vehicle,
)


class ParkingRecordContractTests(TestCase):
    maxDiff = None

    def test_should_match_entry_schema__when_entry_created(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "69가-3455", "slot_id": slot.slot_id}),
            content_type="application/json",
        )

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

    def test_should_match_exit_schema__when_exit_completed(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now() - timedelta(hours=1)
        history = create_active_history(slot=slot, vehicle_num=vehicle.vehicle_num, entry_at=entry_at)
        SlotOccupancy.objects.create(
            slot=slot,
            occupied=True,
            vehicle_num=vehicle.vehicle_num,
            history=history,
            occupied_at=entry_at,
        )

        # When
        response = self.client.post(
            "/api/parking/exit",
            data=json.dumps({"vehicle_num": vehicle.vehicle_num}),
            content_type="application/json",
        )

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

    def test_should_expose_write_fields_only__when_command_succeeds(self) -> None:
        # Given
        create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "69가-3455", "slot_id": slot.slot_id}),
            content_type="application/json",
        )

        # Then
        body = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("zone_name", body)
        self.assertNotIn("slot_name", body)
        self.assertNotIn("available_count", body)

    def test_should_preserve_bad_request__when_command_schema_invalid(self) -> None:
        # Given
        create_vehicle()

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "invalid"}),
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
                    "details": {
                        "vehicle_num": ["지원하지 않는 차량 번호 형식입니다."],
                        "slot_id": ["필수 입력값입니다."],
                    },
                }
            },
        )

    def test_should_preserve_not_found__when_resource_missing(self) -> None:
        # Given
        create_vehicle()

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "69가3455", "slot_id": 9999}),
            content_type="application/json",
        )

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

    def test_should_preserve_conflict__when_entry_precondition_invalid(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot(is_active=False)
        create_empty_occupancy(slot=slot)

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": vehicle.vehicle_num, "slot_id": slot.slot_id}),
            content_type="application/json",
        )

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

    def test_should_preserve_error_contract__when_exit_time_invalid(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now()
        history = create_active_history(slot=slot, vehicle_num=vehicle.vehicle_num, entry_at=entry_at)
        SlotOccupancy.objects.create(
            slot=slot,
            occupied=True,
            vehicle_num=vehicle.vehicle_num,
            history=history,
            occupied_at=entry_at,
        )

        # When
        response = self.client.post(
            "/api/parking/exit",
            data=json.dumps(
                {
                    "vehicle_num": vehicle.vehicle_num,
                    "exit_at": (entry_at - timedelta(minutes=1)).isoformat(),
                }
            ),
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
                    "details": ["출차 시각은 입차 시각보다 빠를 수 없습니다."],
                }
            },
        )
