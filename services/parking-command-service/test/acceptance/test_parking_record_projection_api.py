from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

from parking_command_service.domains.parking_record.infrastructure.repositories import (
    DjangoParkingProjectionWriter,
)
from parking_query_service.models import CurrentParkingView, ZoneAvailability

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from support.api import post_entry, post_exit  # noqa: E402
from support.factories import (  # noqa: E402
    create_empty_occupancy,
    create_occupied_session,
    create_slot,
    create_vehicle,
)


# projection API 인수 테스트 클래스
class ParkingRecordProjectionAcceptanceTests(TestCase):
    # 입차 후 현재 위치 projection 생성 검증
    def test_should_create_query_projection__when_entry_api_succeeds(self) -> None:
        # Given
        vehicle = create_vehicle()
        target_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        create_empty_occupancy(slot=target_slot)
        create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A002")

        # When
        response = post_entry(self.client, vehicle_num=vehicle.vehicle_num, slot_id=target_slot.slot_id)

        # Then
        self.assertEqual(response.status_code, 201)
        current_view = CurrentParkingView.objects.get(vehicle_num=vehicle.vehicle_num)
        zone_availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")
        self.assertEqual(current_view.slot_id, target_slot.slot_id)
        self.assertEqual(zone_availability.total_count, 2)
        self.assertEqual(zone_availability.occupied_count, 1)
        self.assertEqual(zone_availability.available_count, 1)

    # 출차 후 현재 위치 projection 제거 검증
    def test_should_remove_query_projection__when_exit_api_succeeds(self) -> None:
        # Given
        vehicle = create_vehicle()
        target_slot = create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A001")
        create_slot(zone_id=1, slot_type_id=1, slot_type_name="GENERAL", slot_code="A002")
        history, _occupancy = create_occupied_session(
            slot=target_slot,
            vehicle_num=vehicle.vehicle_num,
            entry_at=timezone.now() - timedelta(hours=2),
        )
        DjangoParkingProjectionWriter().record_entry(history=history)

        # When
        response = post_exit(self.client, vehicle_num=vehicle.vehicle_num, exit_at=timezone.now())

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CurrentParkingView.objects.filter(vehicle_num=vehicle.vehicle_num).exists())
        zone_availability = ZoneAvailability.objects.get(zone_id=1, slot_type="GENERAL")
        self.assertEqual(zone_availability.total_count, 2)
        self.assertEqual(zone_availability.occupied_count, 0)
        self.assertEqual(zone_availability.available_count, 2)
