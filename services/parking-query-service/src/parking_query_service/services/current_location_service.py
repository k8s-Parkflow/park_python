from http import HTTPStatus
from typing import Any

from park_py.error_handling.error_codes import ErrorCode
from park_py.error_handling.exceptions import ApplicationError
from parking_query_service.vehicle_num import normalize_vehicle_num


class VehicleNotFoundError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            "존재하지 않는 차량입니다.",
            code=ErrorCode.NOT_FOUND,
            status=HTTPStatus.NOT_FOUND,
        )


class CurrentVehicleNotParkedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            "현재 주차 중인 차량이 없습니다.",
            code=ErrorCode.NOT_FOUND,
            status=HTTPStatus.NOT_FOUND,
        )

class CurrentLocationService:
    def __init__(self, *, current_location_repository: Any, vehicle_repository: Any) -> None:
        self._current_location_repository = current_location_repository
        self._vehicle_repository = vehicle_repository

    def get_current_location(self, vehicle_num: str) -> dict:
        current_location = self._current_location_repository.get_by_vehicle_num(
            normalize_vehicle_num(vehicle_num)
        )
        if current_location is None:
            self._raise_missing_location_error(vehicle_num)

        return {
            "vehicle_num": self._value_of(current_location, "vehicle_num"),
            "zone_name": self._value_of(current_location, "zone_name"),
            "slot_name": self._value_of(current_location, "slot_name"),
        }

    def _raise_missing_location_error(self, vehicle_num: str) -> None:
        if not self._vehicle_repository.exists_by_vehicle_num(normalize_vehicle_num(vehicle_num)):
            raise VehicleNotFoundError()
        raise CurrentVehicleNotParkedError()

    @staticmethod
    def _value_of(source: Any, field_name: str):
        if isinstance(source, dict):
            return source[field_name]
        return getattr(source, field_name)
