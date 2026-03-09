from django.db.models import Value
from django.db.models.functions import Replace

from parking_query_service.vehicle_num import normalize_vehicle_num
from vehicle_service.models.vehicle import Vehicle


class VehicleRepository:
    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        normalized_vehicle_num = normalize_vehicle_num(vehicle_num)
        return (
            Vehicle.objects.annotate(
                normalized_vehicle_num=Replace(
                    Replace("vehicle_num", Value("-"), Value("")),
                    Value(" "),
                    Value(""),
                )
            )
            .filter(normalized_vehicle_num=normalized_vehicle_num)
            .exists()
        )
