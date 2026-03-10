from __future__ import annotations

from django.test import TestCase
from django.utils import timezone

from parking_query_service.models import CurrentParkingView
from parking_query_service.repositories.current_location_repository import CurrentLocationRepository


class ParkingQueryGrpcProjectionRepositoryTests(TestCase):
    def test_should_upsert_grpc_projection_fields__when_projection_is_saved(self) -> None:
        """[RT-PQ-GRPC-01] grpc projection 저장"""

        repository = CurrentLocationRepository()
        repository.save_projection(
            {
                "vehicle_num": "12가3456",
                "history_id": 101,
                "zone_id": 1,
                "zone_name": "A-1",
                "slot_id": 7,
                "slot_code": "A001",
                "slot_type": "GENERAL",
                "entry_at": timezone.now(),
            }
        )

        projection = CurrentParkingView.objects.get(vehicle_num="12가3456")
        self.assertEqual(projection.history_id, 101)
        self.assertEqual(projection.zone_id, 1)
        self.assertEqual(projection.zone_name, "A-1")
        self.assertEqual(projection.slot_id, 7)
        self.assertEqual(projection.slot_code, "A001")
        self.assertEqual(projection.slot_name, "A001")

    def test_should_delete_projection__when_vehicle_num_is_removed(self) -> None:
        """[RT-PQ-GRPC-02] grpc projection 삭제"""

        CurrentParkingView.objects.create(
            vehicle_num="12가3456",
            history_id=101,
            zone_id=1,
            slot_id=7,
            slot_type="GENERAL",
            entry_at=timezone.now(),
        )

        CurrentLocationRepository().delete_projection(vehicle_num="12가3456")

        self.assertFalse(CurrentParkingView.objects.filter(vehicle_num="12가3456").exists())
