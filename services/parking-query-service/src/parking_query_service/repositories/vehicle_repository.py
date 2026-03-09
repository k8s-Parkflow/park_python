from parking_query_service.repositories.normalized_vehicle_num import with_normalized_vehicle_num
from parking_query_service.vehicle_num import normalize_vehicle_num
from vehicle_service.models.vehicle import Vehicle


class VehicleRepository:
    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        normalized_vehicle_num = normalize_vehicle_num(vehicle_num)
        return (
            with_normalized_vehicle_num(Vehicle.objects)
            .filter(normalized_vehicle_num=normalized_vehicle_num)
            .exists()
        )
