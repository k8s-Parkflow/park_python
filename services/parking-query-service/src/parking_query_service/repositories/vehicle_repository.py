from django.db.models import Value
from django.db.models.functions import Replace

from vehicle_service.models.vehicle import Vehicle


class VehicleRepository:
    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        normalized_vehicle_num = vehicle_num.replace("-", "").replace(" ", "")
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
