from typing import Any


class CurrentLocationProjectionService:
    def __init__(self, *, current_location_repository: Any) -> None:
        self._current_location_repository = current_location_repository

    def upsert_current_location(self, projection: dict) -> None:
        current_location = self._current_location_repository.get_by_vehicle_num(
            projection["vehicle_num"]
        )
        if current_location is not None and self._is_stale(
            incoming_updated_at=projection["updated_at"],
            current_updated_at=self._value_of(current_location, "updated_at"),
        ):
            return

        self._current_location_repository.save(projection)

    def remove_current_location(self, vehicle_num: str, updated_at) -> None:
        current_location = self._current_location_repository.get_by_vehicle_num(vehicle_num)
        if current_location is None:
            return
        if self._is_stale(
            incoming_updated_at=updated_at,
            current_updated_at=self._value_of(current_location, "updated_at"),
        ):
            return

        self._current_location_repository.delete_by_vehicle_num(
            self._value_of(current_location, "vehicle_num")
        )

    @staticmethod
    def _is_stale(*, incoming_updated_at, current_updated_at) -> bool:
        return current_updated_at > incoming_updated_at

    @staticmethod
    def _value_of(source: Any, field_name: str):
        if isinstance(source, dict):
            return source[field_name]
        return getattr(source, field_name)
