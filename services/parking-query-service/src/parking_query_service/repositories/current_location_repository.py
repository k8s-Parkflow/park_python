from typing import Optional

from django.db.models import Value
from django.db.models.functions import Replace

from parking_query_service.models.current_parking_view import CurrentParkingView


class CurrentLocationRepository:
    def get_by_vehicle_num(self, vehicle_num: str) -> Optional[CurrentParkingView]:
        normalized_vehicle_num = self._normalize_for_lookup(vehicle_num)
        return (
            CurrentParkingView.objects.annotate(
                normalized_vehicle_num=Replace(
                    Replace("vehicle_num", Value("-"), Value("")),
                    Value(" "),
                    Value(""),
                )
            )
            .filter(normalized_vehicle_num=normalized_vehicle_num)
            .first()
        )

    def save(self, projection: dict) -> CurrentParkingView:
        current_location, _ = CurrentParkingView.objects.update_or_create(
            vehicle_num=projection["vehicle_num"],
            defaults={
                "zone_name": projection["zone_name"],
                "slot_name": projection["slot_name"],
                "slot_type": projection["slot_type"],
                "entry_at": projection["entry_at"],
            },
        )
        return current_location

    def delete_by_vehicle_num(self, vehicle_num: str) -> None:
        CurrentParkingView.objects.filter(vehicle_num=vehicle_num).delete()

    @staticmethod
    def _normalize_for_lookup(vehicle_num: str) -> str:
        return vehicle_num.replace("-", "").replace(" ", "")
