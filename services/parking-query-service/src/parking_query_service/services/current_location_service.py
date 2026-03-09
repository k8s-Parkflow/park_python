from http import HTTPStatus
from typing import Mapping, Optional, Protocol, TypedDict, Union

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


class CurrentLocationProjection(Protocol):
    vehicle_num: str
    zone_name: str
    slot_name: str


class CurrentLocationRepositoryProtocol(Protocol):
    def get_by_vehicle_num(
        self, vehicle_num: str
    ) -> Optional[Union[CurrentLocationProjection, Mapping[str, str]]]:
        ...


class VehicleRepositoryProtocol(Protocol):
    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        ...


class CurrentLocationPayload(TypedDict):
    vehicle_num: str
    zone_name: str
    slot_name: str


class CurrentLocationService:
    def __init__(
        self,
        *,
        current_location_repository: CurrentLocationRepositoryProtocol,
        vehicle_repository: VehicleRepositoryProtocol,
    ) -> None:
        self._current_location_repository = current_location_repository
        self._vehicle_repository = vehicle_repository

    def get_current_location(self, vehicle_num: str) -> CurrentLocationPayload:
        normalized_vehicle_num = normalize_vehicle_num(vehicle_num)
        current_location = self._get_current_location_or_raise(normalized_vehicle_num)
        return self._build_location_payload(current_location)

    def _get_current_location_or_raise(
        self, normalized_vehicle_num: str
    ) -> Union[CurrentLocationProjection, Mapping[str, str]]:
        current_location = self._current_location_repository.get_by_vehicle_num(
            normalized_vehicle_num
        )
        if current_location is not None:
            return current_location

        if not self._vehicle_repository.exists_by_vehicle_num(normalized_vehicle_num):
            raise VehicleNotFoundError()
        raise CurrentVehicleNotParkedError()

    def _build_location_payload(
        self, current_location: Union[CurrentLocationProjection, Mapping[str, str]]
    ) -> CurrentLocationPayload:
        return {
            "vehicle_num": self._value_of(current_location, "vehicle_num"),
            "zone_name": self._value_of(current_location, "zone_name"),
            "slot_name": self._value_of(current_location, "slot_name"),
        }

    @staticmethod
    def _value_of(
        source: Union[CurrentLocationProjection, Mapping[str, str]], field_name: str
    ) -> str:
        if isinstance(source, Mapping):
            return source[field_name]
        return getattr(source, field_name)
