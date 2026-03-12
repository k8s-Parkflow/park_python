from __future__ import annotations

from django.db.models import Value
from django.db.models.functions import Replace

from vehicle_service.vehicle.domain.entities import Vehicle


class VehicleRepository:
    def get(self, *, vehicle_num: str) -> Vehicle:
        normalized_vehicle_num = vehicle_num.replace("-", "")
        return (
            Vehicle.objects.annotate(
                normalized_vehicle_num=Replace("vehicle_num", Value("-"), Value("")),
            )
            .get(normalized_vehicle_num=normalized_vehicle_num)
        )
