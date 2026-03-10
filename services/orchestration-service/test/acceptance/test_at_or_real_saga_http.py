from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request
from urllib.request import urlopen

from django.test import LiveServerTestCase, override_settings
from django.utils.dateparse import parse_datetime

from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingHistoryStatus
from parking_command_service.models import ParkingSlot
from parking_command_service.models import SlotOccupancy
from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ZoneAvailability
from vehicle_service.models.enums import VehicleType
from vehicle_service.models.vehicle import Vehicle
from zone_service.models.slot_type import SlotType
from zone_service.models.zone import Zone


def post_json(url: str, payload: dict, *, headers: dict[str, str] | None = None) -> tuple[int, dict]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method="POST",
    )

    try:
        with urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


@override_settings(ROOT_URLCONF="park_py.urls")
class OrchestrationRealSagaHttpAcceptanceTests(LiveServerTestCase):
    def test_should_complete_entry_saga_over_real_http__when_all_participants_succeed(self) -> None:
        """[AT-OR-REAL-01] 실제 HTTP 기반 입차 성공"""

        zone = Zone.objects.create(zone_name="A")
        slot_type = SlotType.objects.create(type_name="GENERAL")
        Vehicle.objects.create(vehicle_num="12가3456", vehicle_type=VehicleType.General)
        slot = ParkingSlot.objects.create(
            zone_id=zone.zone_id,
            slot_type_id=slot_type.slot_type_id,
            slot_code="A-01",
        )
        SlotOccupancy.objects.create(slot=slot)
        ZoneAvailability.objects.create(
            zone_id=zone.zone_id,
            slot_type="GENERAL",
            total_count=1,
            occupied_count=0,
            available_count=1,
        )

        # Given
        payload = {
            "vehicle_num": "12가3456",
            "slot_id": slot.slot_id,
            "requested_at": "2026-03-10T10:00:00+09:00",
        }

        # When
        status_code, body = post_json(
            f"{self.live_server_url}/api/v1/parking/entries",
            payload,
            headers={"Idempotency-Key": "entry-real-http-001"},
        )

        # Then
        self.assertEqual(status_code, 201)
        self.assertEqual(body["status"], "COMPLETED")

        history = ParkingHistory.objects.get(history_id=body["history_id"])
        occupancy = SlotOccupancy.objects.get(slot=slot)
        projection = CurrentParkingView.objects.get(vehicle_num="12가3456")
        availability = ZoneAvailability.objects.get(zone_id=zone.zone_id, slot_type="GENERAL")

        self.assertEqual(history.status, ParkingHistoryStatus.PARKED)
        self.assertTrue(occupancy.occupied)
        self.assertEqual(projection.slot_id, slot.slot_id)
        self.assertEqual(availability.occupied_count, 1)
        self.assertEqual(availability.available_count, 0)

        replay_status_code, replay_body = post_json(
            f"{self.live_server_url}/api/v1/parking/entries",
            payload,
            headers={"Idempotency-Key": "entry-real-http-001"},
        )

        self.assertEqual(replay_status_code, 201)
        self.assertEqual(replay_body, body)

    def test_should_compensate_entry_over_real_http__when_query_projection_fails(self) -> None:
        """[AT-OR-REAL-02] 실제 HTTP 기반 입차 보상"""

        zone = Zone.objects.create(zone_name="B")
        slot_type = SlotType.objects.create(type_name="GENERAL")
        Vehicle.objects.create(vehicle_num="34나5678", vehicle_type=VehicleType.General)
        slot = ParkingSlot.objects.create(
            zone_id=zone.zone_id,
            slot_type_id=slot_type.slot_type_id,
            slot_code="B-01",
        )
        SlotOccupancy.objects.create(slot=slot)

        # Given
        payload = {
            "vehicle_num": "34나5678",
            "slot_id": slot.slot_id,
            "requested_at": "2026-03-10T11:00:00+09:00",
        }

        # When
        status_code, body = post_json(
            f"{self.live_server_url}/api/v1/parking/entries",
            payload,
            headers={"Idempotency-Key": "entry-real-http-002"},
        )

        # Then
        self.assertEqual(status_code, 409)
        self.assertEqual(body["error"]["details"]["status"], "COMPENSATED")
        self.assertFalse(ParkingHistory.objects.filter(vehicle_num="34나5678", exit_at__isnull=True).exists())
        self.assertFalse(CurrentParkingView.objects.filter(vehicle_num="34나5678").exists())

        occupancy = SlotOccupancy.objects.get(slot=slot)
        self.assertFalse(occupancy.occupied)
        self.assertIsNone(occupancy.vehicle_num)
        self.assertIsNone(occupancy.history)

        replay_status_code, replay_body = post_json(
            f"{self.live_server_url}/api/v1/parking/entries",
            payload,
            headers={"Idempotency-Key": "entry-real-http-002"},
        )

        self.assertEqual(replay_status_code, 409)
        self.assertEqual(replay_body, body)

    def test_should_complete_exit_saga_over_real_http__when_all_participants_succeed(self) -> None:
        """[AT-OR-REAL-03] 실제 HTTP 기반 출차 성공"""

        zone = Zone.objects.create(zone_name="C")
        slot_type = SlotType.objects.create(type_name="GENERAL")
        Vehicle.objects.create(vehicle_num="56다7890", vehicle_type=VehicleType.General)
        slot = ParkingSlot.objects.create(
            zone_id=zone.zone_id,
            slot_type_id=slot_type.slot_type_id,
            slot_code="C-01",
        )
        history = ParkingHistory.start(
            slot=slot,
            vehicle_num="56다7890",
            entry_at=parse_datetime("2026-03-10T10:00:00+09:00"),
        )
        history.save()
        SlotOccupancy.objects.create(
            slot=slot,
            occupied=True,
            vehicle_num="56다7890",
            history=history,
            occupied_at=history.entry_at,
        )
        CurrentParkingView.objects.create(
            vehicle_num="56다7890",
            slot_id=slot.slot_id,
            zone_id=zone.zone_id,
            slot_type="GENERAL",
            entry_at=history.entry_at,
        )
        ZoneAvailability.objects.create(
            zone_id=zone.zone_id,
            slot_type="GENERAL",
            total_count=1,
            occupied_count=1,
            available_count=0,
        )

        # Given
        payload = {
            "vehicle_num": "56다7890",
            "requested_at": "2026-03-10T12:00:00+09:00",
        }

        # When
        status_code, body = post_json(
            f"{self.live_server_url}/api/v1/parking/exits",
            payload,
            headers={"Idempotency-Key": "exit-real-http-001"},
        )

        # Then
        self.assertEqual(status_code, 200)
        self.assertEqual(body["status"], "COMPLETED")

        history.refresh_from_db()
        occupancy = SlotOccupancy.objects.get(slot=slot)
        availability = ZoneAvailability.objects.get(zone_id=zone.zone_id, slot_type="GENERAL")

        self.assertEqual(history.status, ParkingHistoryStatus.EXITED)
        self.assertFalse(occupancy.occupied)
        self.assertFalse(CurrentParkingView.objects.filter(vehicle_num="56다7890").exists())
        self.assertEqual(availability.occupied_count, 0)
        self.assertEqual(availability.available_count, 1)
