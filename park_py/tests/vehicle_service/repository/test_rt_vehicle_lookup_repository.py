from __future__ import annotations

from django.test import TestCase

from vehicle_service.models import Vehicle
from vehicle_service.models.enums import VehicleType
from vehicle_service.repositories.vehicle import VehicleRepository


class VehicleLookupRepositoryTests(TestCase):
    def test_should_return_vehicle__when_vehicle_num_exists(self) -> None:
        """[RT-VEHICLE-GRPC-01] 차량 조회 저장소"""

        # Given
        Vehicle.objects.create(vehicle_num="12가3456", vehicle_type=VehicleType.General)

        # When
        vehicle = VehicleRepository().get(vehicle_num="12가3456")

        # Then
        self.assertEqual(vehicle.vehicle_num, "12가3456")
        self.assertEqual(vehicle.vehicle_type, "GENERAL")

    def test_should_return_vehicle__when_vehicle_num_is_normalized(self) -> None:
        """[RT-VEHICLE-GRPC-02] 차량번호 정규화 조회"""

        Vehicle.objects.create(vehicle_num="12가-3456", vehicle_type=VehicleType.General)

        vehicle = VehicleRepository().get(vehicle_num="12가3456")

        self.assertEqual(vehicle.vehicle_num, "12가-3456")
