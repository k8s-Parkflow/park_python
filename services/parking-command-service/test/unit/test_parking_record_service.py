from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from parking_command_service.dtos import EntryCommand, ExitCommand
from parking_command_service.models import ParkingHistory, ParkingSlot, SlotOccupancy
from parking_command_service.models.enums import ParkingHistoryStatus
from parking_command_service.services import ParkingRecordCommandService

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))


class ParkingRecordServiceUnitTests(TestCase):
    def test_should_create_history_and_occupancy__when_entry_service_called(self) -> None:
        # Given
        entry_at = timezone.now()
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        occupancy = SlotOccupancy(slot=slot)
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        vehicle_repository.exists.return_value = True
        parking_record_repository.get_slot_for_update.return_value = slot
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.has_active_history_for_vehicle.return_value = False

        def assign_history_id(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = assign_history_id
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy

        service = ParkingRecordCommandService(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_entry(
            command=EntryCommand(vehicle_num="69가3455", slot_id=slot.slot_id, entry_at=entry_at)
        )

        # Then
        self.assertEqual(snapshot.history_id, 101)
        self.assertEqual(snapshot.vehicle_num, "69가3455")
        self.assertEqual(snapshot.slot_id, slot.slot_id)
        self.assertEqual(snapshot.status, ParkingHistoryStatus.PARKED)
        self.assertEqual(snapshot.entry_at, entry_at)
        self.assertIsNone(snapshot.exit_at)
        self.assertTrue(occupancy.occupied)
        parking_record_repository.save_history.assert_called_once()
        parking_record_repository.save_occupancy.assert_called_once()

    def test_should_exit_history_and_release_occupancy__when_exit_service_called(self) -> None:
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
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.save_history.side_effect = lambda *, history: history
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy

        service = ParkingRecordCommandService(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_exit(command=ExitCommand(vehicle_num="69가3455", exit_at=exit_at))

        # Then
        self.assertEqual(snapshot.history_id, 101)
        self.assertEqual(snapshot.status, ParkingHistoryStatus.EXITED)
        self.assertEqual(snapshot.exit_at, exit_at)
        self.assertFalse(occupancy.occupied)
        self.assertIsNone(occupancy.vehicle_num)
        parking_record_repository.save_history.assert_called_once()
        parking_record_repository.save_occupancy.assert_called_once()

    def test_should_map_write_snapshot_only__when_building_command_response(self) -> None:
        # Given
        entry_at = timezone.now()
        slot = ParkingSlot(slot_id=1, zone_id=1, slot_type_id=1, slot_code="A001", is_active=True)
        occupancy = SlotOccupancy(slot=slot)
        parking_record_repository = Mock()
        vehicle_repository = Mock()
        vehicle_repository.exists.return_value = True
        parking_record_repository.get_slot_for_update.return_value = slot
        parking_record_repository.get_or_create_occupancy_for_update.return_value = occupancy
        parking_record_repository.has_active_history_for_vehicle.return_value = False

        def assign_history_id(*, history: ParkingHistory) -> ParkingHistory:
            history.history_id = 101
            return history

        parking_record_repository.save_history.side_effect = assign_history_id
        parking_record_repository.save_occupancy.side_effect = lambda *, occupancy: occupancy
        service = ParkingRecordCommandService(
            parking_record_repository=parking_record_repository,
            vehicle_repository=vehicle_repository,
        )

        # When
        snapshot = service.create_entry(
            command=EntryCommand(vehicle_num="69가3455", slot_id=slot.slot_id, entry_at=entry_at)
        )

        # Then
        self.assertSetEqual(
            set(snapshot.to_dict().keys()),
            {"history_id", "vehicle_num", "slot_id", "status", "entry_at", "exit_at"},
        )
