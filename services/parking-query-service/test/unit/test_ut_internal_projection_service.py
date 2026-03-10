from unittest.mock import Mock, patch

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from park_py.error_handling import ApplicationError
from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ZoneAvailability
from parking_query_service.services.internal_projection_service import _claim_operation_record
from parking_query_service.services.internal_projection_service import project_exit


class InternalProjectionServiceUnitTests(TestCase):
    def test_should_reuse_cached_response__when_query_operation_claim_conflicts(self) -> None:
        """[UT-PQ-INT-01] query operation 선점 충돌 시 기존 응답 재사용"""

        existing_record = Mock(response_payload={"projected": True})

        with patch("parking_query_service.services.internal_projection_service.ParkingQueryOperation.objects") as manager:
            manager.create.side_effect = IntegrityError()
            manager.select_for_update.return_value.get.return_value = existing_record

            record, cached_response = _claim_operation_record(
                operation_id="projection-op-001",
                action="PROJECT_EXIT",
            )

        self.assertIs(record, existing_record)
        self.assertEqual(cached_response, {"projected": True})

    def test_should_fail_fast__when_query_operation_is_still_in_progress(self) -> None:
        """[UT-PQ-INT-02] 미완료 query operation 재진입 차단"""

        existing_record = Mock(response_payload=None)

        with patch("parking_query_service.services.internal_projection_service.ParkingQueryOperation.objects") as manager:
            manager.create.side_effect = IntegrityError()
            manager.select_for_update.return_value.get.return_value = existing_record

            with self.assertRaises(ApplicationError) as context:
                _claim_operation_record(
                    operation_id="projection-op-002",
                    action="PROJECT_EXIT",
                )

        self.assertEqual(context.exception.status, 409)
        self.assertEqual(
            context.exception.details,
            {
                "error_code": "operation_in_progress",
                "operation_id": "projection-op-002",
                "action": "PROJECT_EXIT",
            },
        )

    def test_should_reject_exit_projection__when_occupied_count_would_underflow(self) -> None:
        """[UT-PQ-INT-03] 출차 projection count underflow 방어"""

        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=10,
            occupied_count=0,
            available_count=10,
        )
        CurrentParkingView.objects.create(
            vehicle_num="12가3456",
            zone_id=1,
            slot_id=7,
            slot_type="GENERAL",
            entry_at=timezone.now(),
        )

        with self.assertRaises(ApplicationError) as context:
            project_exit(operation_id="project-exit-001", vehicle_num="12가3456")

        availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")
        self.assertEqual(context.exception.status, 409)
        self.assertEqual(
            context.exception.details,
            {
                "error_code": "projection_count_underflow",
                "zone_id": 1,
                "slot_type": "GENERAL",
            },
        )
        self.assertEqual(availability.occupied_count, 0)
        self.assertTrue(CurrentParkingView.objects.filter(vehicle_num="12가3456").exists())
