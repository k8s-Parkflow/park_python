from __future__ import annotations

from vehicle_service.models import Vehicle
from vehicle_service.repositories.vehicle import VehicleRepository


class VehicleLookupService:
    def __init__(self, *, vehicle_repository: VehicleRepository | None = None) -> None:
        self.vehicle_repository = vehicle_repository or VehicleRepository()

    def get_vehicle(self, *, vehicle_num: str) -> Vehicle:
        return self.vehicle_repository.get(vehicle_num=vehicle_num)
