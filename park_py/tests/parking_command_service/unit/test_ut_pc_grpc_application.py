from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock

from django.test import TestCase

from parking_command_service.domains.parking_record.application.dtos import ParkingRecordSnapshot
from parking_command_service.grpc.application import ParkingCommandGrpcApplicationService


class ParkingCommandGrpcApplicationUnitTests(TestCase):
    def test_should_build_entry_command_from_slot__when_create_entry_is_called(self) -> None:
        """[UT-PC-GRPC-01] slot 기반 create-entry command 조립"""

        # Given
        slot = Mock(zone_id=1, slot_code="A001", slot_id=7)
        repository = Mock()
        repository.get_slot.return_value = slot
        command_service = Mock()
        command_service.create_entry.return_value = ParkingRecordSnapshot(
            history_id=101,
            vehicle_num="12가3456",
            zone_id=1,
            slot_code="A001",
            slot_id=7,
            status="PARKED",
            entry_at=datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
            exit_at=None,
        )
        service = ParkingCommandGrpcApplicationService(
            parking_record_repository=repository,
            command_service=command_service,
        )

        # When
        snapshot = service.create_entry(
            vehicle_num="12가3456",
            slot_id=7,
            requested_at=datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
        )

        # Then
        self.assertEqual(snapshot.history_id, 101)
        command = command_service.create_entry.call_args.kwargs["command"]
        self.assertEqual(command.zone_id, 1)
        self.assertEqual(command.slot_code, "A001")

    def test_should_return_existing_compensation_result__when_entry_is_already_released(self) -> None:
        """[UT-PC-GRPC-02] compensate-entry 멱등 처리"""

        # Given
        history = Mock(history_id=101, exit_at=datetime(2026, 3, 10, 1, 5, tzinfo=timezone.utc))
        history.slot = Mock()
        occupancy = Mock(occupied=False)
        repository = Mock()
        repository.get_history_for_update.return_value = history
        repository.get_or_create_occupancy_for_update.return_value = occupancy
        service = ParkingCommandGrpcApplicationService(
            parking_record_repository=repository,
            command_service=Mock(),
        )

        # When
        payload = service.compensate_entry(history_id=101)

        # Then
        self.assertEqual(payload["history_id"], 101)
        self.assertTrue(payload["slot_released"])
        repository.save_history.assert_not_called()
        repository.save_occupancy.assert_not_called()

    def test_should_build_exit_command_from_active_history__when_create_exit_is_called(self) -> None:
        """[UT-PC-GRPC-03] active-history 기반 exit command 조립"""

        # Given
        history = Mock()
        history.slot = Mock(zone_id=1, slot_code="A001")
        history.slot_id = 7
        repository = Mock()
        repository.get_active_history_for_vehicle.return_value = history
        command_service = Mock()
        command_service.create_exit.return_value = ParkingRecordSnapshot(
            history_id=101,
            vehicle_num="12가3456",
            zone_id=1,
            slot_code="A001",
            slot_id=7,
            status="EXITED",
            entry_at=datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
            exit_at=datetime(2026, 3, 10, 3, 0, tzinfo=timezone.utc),
        )
        service = ParkingCommandGrpcApplicationService(
            parking_record_repository=repository,
            command_service=command_service,
        )

        # When
        snapshot = service.exit_parking(
            vehicle_num="12가3456",
            requested_at=datetime(2026, 3, 10, 3, 0, tzinfo=timezone.utc),
        )

        # Then
        self.assertEqual(snapshot.status, "EXITED")
        command = command_service.create_exit.call_args.kwargs["command"]
        self.assertEqual(command.zone_id, 1)
        self.assertEqual(command.slot_code, "A001")

    def test_should_restore_active_parking__when_compensate_exit_is_called(self) -> None:
        """[UT-PC-GRPC-04] compensate-exit 복원 처리"""

        # Given
        history = Mock(
            history_id=101,
            vehicle_num="12가3456",
            entry_at=datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
            exit_at=datetime(2026, 3, 10, 3, 0, tzinfo=timezone.utc),
        )
        history.slot = Mock()
        occupancy = Mock(occupied=False)
        repository = Mock()
        repository.get_history_for_update.return_value = history
        repository.get_or_create_occupancy_for_update.return_value = occupancy
        service = ParkingCommandGrpcApplicationService(
            parking_record_repository=repository,
            command_service=Mock(),
        )

        # When
        payload = service.compensate_exit(history_id=101)

        # Then
        self.assertEqual(payload["history_id"], 101)
        self.assertTrue(payload["slot_occupied"])
        history.cancel_exit.assert_called_once()
        occupancy.restore.assert_called_once()
