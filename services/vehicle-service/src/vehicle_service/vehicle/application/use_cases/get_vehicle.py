from __future__ import annotations

from vehicle_service.vehicle.domain.entities import Vehicle
from vehicle_service.vehicle.infrastructure.repositories.vehicle import VehicleRepository


class VehicleLookupService:
    def __init__(self, *, vehicle_repository: VehicleRepository | None = None) -> None:
        self.vehicle_repository = vehicle_repository or VehicleRepository()

    def get_vehicle(self, *, vehicle_num: str) -> Vehicle:
        return self.vehicle_repository.get(vehicle_num=vehicle_num)
