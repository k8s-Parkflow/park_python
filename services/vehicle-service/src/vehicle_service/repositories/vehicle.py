from __future__ import annotations

from vehicle_service.models import Vehicle


class VehicleRepository:
    def get(self, *, vehicle_num: str) -> Vehicle:
        return Vehicle.objects.get(vehicle_num=vehicle_num)
