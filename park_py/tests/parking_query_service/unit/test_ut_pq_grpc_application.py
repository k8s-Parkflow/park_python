from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import Mock

from django.test import SimpleTestCase

from parking_query_service.grpc.application import ParkingQueryGrpcApplicationService


class ParkingQueryGrpcApplicationUnitTests(SimpleTestCase):
    def test_should_apply_entry_projection__when_called(self) -> None:
        """[UT-PQ-GRPC-01] apply-entry projection 저장 위임"""

        repository = Mock()
        service = ParkingQueryGrpcApplicationService(current_location_repository=repository)

        payload = service.apply_entry_projection(
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            entry_at=datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
        )

        self.assertTrue(payload["projected"])
        repository.save_projection.assert_called_once()

    def test_should_restore_projection__when_compensate_exit_projection_is_called(self) -> None:
        """[UT-PQ-GRPC-02] compensate-exit projection 복원"""

        repository = Mock()
        service = ParkingQueryGrpcApplicationService(current_location_repository=repository)

        payload = service.compensate_exit_projection(
            history_id=101,
            vehicle_num="12가3456",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            entry_at=datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc),
        )

        self.assertTrue(payload["compensated"])
        repository.save_projection.assert_called_once()
