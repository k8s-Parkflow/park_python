from django.test import TestCase
from django.utils import timezone

from park_py.error_handling import ApplicationError
from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ZoneAvailability
from parking_query_service.services.internal_projection_service import project_exit


class InternalProjectionServiceUnitTests(TestCase):
    def test_should_reject_exit_projection__when_occupied_count_would_underflow(self) -> None:
        """[UT-PQ-INT-01] 출차 projection count underflow 방어"""

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
