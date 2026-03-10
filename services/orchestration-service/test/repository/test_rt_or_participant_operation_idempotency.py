from __future__ import annotations

import sys
from pathlib import Path

from django.test import TestCase

from parking_command_service.models import ParkingHistory
from parking_command_service.models import ParkingSlot
from parking_command_service.models import SlotOccupancy
from parking_query_service.models import CurrentParkingView
from parking_query_service.models import ZoneAvailability
from zone_service.models.slot_type import SlotType
from zone_service.models.zone import Zone


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class ParticipantOperationIdempotencyTests(TestCase):
    def test_should_reuse_cached_entry_result__when_same_command_operation_retries(self) -> None:
        """[RT-OR-PART-01] command write 멱등성"""

        from parking_command_service.services import enter_parking

        zone = Zone.objects.create(zone_name="IDEMP-A")
        slot_type = SlotType.objects.create(type_name="GENERAL")
        slot = ParkingSlot.objects.create(
            zone_id=zone.zone_id,
            slot_type_id=slot_type.slot_type_id,
            slot_code="A-01",
        )
        SlotOccupancy.objects.create(slot=slot)

        first = enter_parking(
            operation_id="entry-op-dup-001",
            vehicle_num="12가3456",
            slot_id=slot.slot_id,
            requested_at="2026-03-10T10:00:00+09:00",
        )

        second = enter_parking(
            operation_id="entry-op-dup-001",
            vehicle_num="12가3456",
            slot_id=slot.slot_id,
            requested_at="2026-03-10T10:00:00+09:00",
        )

        self.assertEqual(second, first)
        self.assertEqual(ParkingHistory.objects.filter(vehicle_num="12가3456", exit_at__isnull=True).count(), 1)

    def test_should_skip_duplicate_restore_count_update__when_same_query_compensation_retries(self) -> None:
        """[RT-OR-PART-02] query compensation 멱등성"""

        from parking_query_service.services import restore_exit

        ZoneAvailability.objects.create(
            zone_id=1,
            slot_type="GENERAL",
            total_count=1,
            occupied_count=0,
            available_count=1,
        )

        first = restore_exit(
            operation_id="exit-comp-dup-001",
            vehicle_num="34나5678",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            entry_at="2026-03-10T10:00:00+09:00",
        )

        second = restore_exit(
            operation_id="exit-comp-dup-001",
            vehicle_num="34나5678",
            slot_id=7,
            zone_id=1,
            slot_type="GENERAL",
            entry_at="2026-03-10T10:00:00+09:00",
        )

        availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")

        self.assertEqual(second, first)
        self.assertEqual(CurrentParkingView.objects.filter(vehicle_num="34나5678").count(), 1)
        self.assertEqual(availability.occupied_count, 1)
        self.assertEqual(availability.available_count, 0)
