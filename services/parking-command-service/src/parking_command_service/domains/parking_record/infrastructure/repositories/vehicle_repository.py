from __future__ import annotations

from vehicle_service.models import Vehicle


class DjangoVehicleRepository:
    def exists(self, *, vehicle_num: str) -> bool:
        return Vehicle.objects.filter(vehicle_num=vehicle_num).exists()
