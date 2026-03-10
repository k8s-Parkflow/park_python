from typing import Optional

from parking_query_service.models.current_parking_view import CurrentParkingView
from parking_query_service.repositories.normalized_vehicle_num import with_normalized_vehicle_num
from parking_query_service.vehicle_num import normalize_vehicle_num


class CurrentLocationRepository:
    def get_by_vehicle_num(self, vehicle_num: str) -> Optional[CurrentParkingView]:
        normalized_vehicle_num = self._normalize_for_lookup(vehicle_num)
        return (
            with_normalized_vehicle_num(CurrentParkingView.objects)
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

    def save_projection(self, projection: dict) -> CurrentParkingView:
        current_location, _ = CurrentParkingView.objects.update_or_create(
            vehicle_num=projection["vehicle_num"],
            defaults={
                "history_id": projection["history_id"],
                "zone_id": projection["zone_id"],
                "slot_id": projection["slot_id"],
                "slot_type": projection["slot_type"],
                "entry_at": projection["entry_at"],
            },
        )
        return current_location

    def delete_by_vehicle_num(self, vehicle_num: str) -> None:
        CurrentParkingView.objects.filter(vehicle_num=vehicle_num).delete()

    def delete_projection(self, *, vehicle_num: str) -> None:
        self.delete_by_vehicle_num(vehicle_num)

    @staticmethod
    def _normalize_for_lookup(vehicle_num: str) -> str:
        return normalize_vehicle_num(vehicle_num)
