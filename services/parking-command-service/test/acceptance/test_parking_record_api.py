from __future__ import annotations

import json
import sys
import threading
from datetime import timedelta
from pathlib import Path

from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from parking_command_service.models import ParkingHistory, SlotOccupancy
from parking_command_service.models.enums import ParkingHistoryStatus

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from support.factories import (
    create_active_history,
    create_empty_occupancy,
    create_slot,
    create_vehicle,
)


class ParkingRecordAcceptanceTests(TestCase):
    maxDiff = None

    def test_should_create_active_history_and_occupancy__when_entry_requested(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)
        entry_at = timezone.now()

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps(
                {
                    "vehicle_num": "69가-3455",
                    "slot_id": slot.slot_id,
                    "entry_at": entry_at.isoformat(),
                }
            ),
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "history_id": ParkingHistory.objects.get().history_id,
                "vehicle_num": vehicle.vehicle_num,
                "slot_id": slot.slot_id,
                "status": "PARKED",
                "entry_at": entry_at.isoformat(),
                "exit_at": None,
            },
        )
        history = ParkingHistory.objects.get()
        occupancy = SlotOccupancy.objects.get(slot=slot)
        self.assertEqual(history.status, ParkingHistoryStatus.PARKED)
        self.assertTrue(occupancy.occupied)
        self.assertEqual(occupancy.vehicle_num, vehicle.vehicle_num)
        self.assertEqual(occupancy.history_id, history.history_id)

    def test_should_close_history_and_release_occupancy__when_exit_requested(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot()
        entry_at = timezone.now() - timedelta(hours=3)
        exit_at = timezone.now()
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
                    "vehicle_num": "69가-3455",
                    "exit_at": exit_at.isoformat(),
                }
            ),
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "history_id": history.history_id,
                "vehicle_num": vehicle.vehicle_num,
                "slot_id": slot.slot_id,
                "status": "EXITED",
                "entry_at": entry_at.isoformat(),
                "exit_at": exit_at.isoformat(),
            },
        )
        history.refresh_from_db()
        occupancy = SlotOccupancy.objects.get(slot=slot)
        self.assertEqual(history.status, ParkingHistoryStatus.EXITED)
        self.assertEqual(history.exit_at, exit_at)
        self.assertFalse(occupancy.occupied)
        self.assertIsNone(occupancy.vehicle_num)
        self.assertIsNone(occupancy.history_id)
        self.assertIsNone(occupancy.occupied_at)

    def test_should_return_not_found__when_vehicle_missing_on_entry(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "69가-3455", "slot_id": slot.slot_id}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertEqual(ParkingHistory.objects.count(), 0)

    def test_should_return_not_found__when_slot_missing_on_entry(self) -> None:
        # Given
        create_vehicle()

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "69가-3455", "slot_id": 9999}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")
        self.assertEqual(ParkingHistory.objects.count(), 0)

    def test_should_return_conflict__when_slot_unavailable_on_entry(self) -> None:
        # Given
        vehicle = create_vehicle()
        slot = create_slot(is_active=False)
        create_empty_occupancy(slot=slot)

        # When
        inactive_response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": vehicle.vehicle_num, "slot_id": slot.slot_id}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(inactive_response.status_code, 409)
        self.assertEqual(inactive_response.json()["error"]["code"], "conflict")

        # Given
        slot.activate()
        slot.save(update_fields=["is_active", "updated_at"])
        occupied_history = create_active_history(
            slot=slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=1),
        )
        occupancy = SlotOccupancy.objects.get(slot=slot)
        occupancy.occupied = True
        occupancy.vehicle_num = vehicle.vehicle_num
        occupancy.history = occupied_history
        occupancy.occupied_at = occupied_history.entry_at
        occupancy.save()
        another_vehicle = create_vehicle(vehicle_num="70가1234")

        # When
        occupied_response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": another_vehicle.vehicle_num, "slot_id": slot.slot_id}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(occupied_response.status_code, 409)
        self.assertEqual(occupied_response.json()["error"]["code"], "conflict")

    def test_should_return_conflict__when_vehicle_already_parked(self) -> None:
        # Given
        vehicle = create_vehicle()
        current_slot = create_slot(slot_code="A001")
        create_empty_occupancy(slot=current_slot)
        current_history = create_active_history(
            slot=current_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=2),
        )
        occupancy = SlotOccupancy.objects.get(slot=current_slot)
        occupancy.occupied = True
        occupancy.vehicle_num = vehicle.vehicle_num
        occupancy.history = current_history
        occupancy.occupied_at = current_history.entry_at
        occupancy.save()

        target_slot = create_slot(slot_code="A002")
        create_empty_occupancy(slot=target_slot)

        # When
        response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": vehicle.vehicle_num, "slot_id": target_slot.slot_id}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "conflict")
        self.assertEqual(ParkingHistory.objects.filter(exit_at__isnull=True).count(), 1)

    def test_should_return_not_found__when_active_history_missing_on_exit(self) -> None:
        # Given
        create_vehicle()

        # When
        response = self.client.post(
            "/api/parking/exit",
            data=json.dumps({"vehicle_num": "69가-3455"}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_should_return_bad_request__when_command_payload_invalid(self) -> None:
        # Given
        create_vehicle()
        slot = create_slot()
        create_empty_occupancy(slot=slot)

        # When
        missing_slot_response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "69가-3455"}),
            content_type="application/json",
        )
        invalid_vehicle_response = self.client.post(
            "/api/parking/entry",
            data=json.dumps({"vehicle_num": "invalid", "slot_id": slot.slot_id}),
            content_type="application/json",
        )
        naive_datetime_response = self.client.post(
            "/api/parking/exit",
            data=json.dumps({"vehicle_num": "69가-3455", "exit_at": "2026-03-09T12:10:00"}),
            content_type="application/json",
        )

        # Then
        self.assertEqual(missing_slot_response.status_code, 400)
        self.assertEqual(invalid_vehicle_response.status_code, 400)
        self.assertEqual(naive_datetime_response.status_code, 400)

    def test_should_reject_exit__when_exit_at_before_entry_at(self) -> None:
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
        self.assertEqual(response.json()["error"]["code"], "bad_request")


class ParkingRecordConcurrencyAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_should_allow_only_one_entry__when_concurrent_requests_compete(self) -> None:
        # Given
        slot = create_slot()
        create_empty_occupancy(slot=slot)
        create_vehicle(vehicle_num="69가3455")
        create_vehicle(vehicle_num="70가1234")
        barrier = threading.Barrier(2)
        responses: list[int] = []

        def request_entry(vehicle_num: str) -> None:
            client = Client()
            barrier.wait()
            response = client.post(
                "/api/parking/entry",
                data=json.dumps({"vehicle_num": vehicle_num, "slot_id": slot.slot_id}),
                content_type="application/json",
            )
            responses.append(response.status_code)

        # When
        first = threading.Thread(target=request_entry, args=("69가3455",))
        second = threading.Thread(target=request_entry, args=("70가1234",))
        first.start()
        second.start()
        first.join()
        second.join()

        # Then
        self.assertCountEqual(responses, [201, 409])
        self.assertEqual(ParkingHistory.objects.filter(exit_at__isnull=True).count(), 1)
        self.assertEqual(SlotOccupancy.objects.filter(occupied=True).count(), 1)
