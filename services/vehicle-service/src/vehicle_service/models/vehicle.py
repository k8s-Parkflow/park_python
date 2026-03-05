from django.db import models

from vehicle_service.models.enums import VehicleType


class Vehicle(models.Model):

    vehicle_num = models.CharField(max_length=20, primary_key=True)
    vehicle_type = models.CharField(max_length=16, choices=VehicleType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "VEHICLE"

    def change_type(self, vehicle_type: VehicleType) -> None:
        self.vehicle_type = vehicle_type
