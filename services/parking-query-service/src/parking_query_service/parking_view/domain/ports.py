from typing import Any, Mapping, Optional, Protocol, Union


class CurrentLocationProjection(Protocol):
    vehicle_num: str
    zone_name: str
    slot_name: str


CurrentLocationSource = Union[CurrentLocationProjection, Mapping[str, str]]


class CurrentLocationRepositoryProtocol(Protocol):
    def get_by_vehicle_num(
        self, vehicle_num: str
    ) -> Optional[CurrentLocationSource]:
        ...


class VehicleLookupPort(Protocol):
    def exists_by_vehicle_num(self, vehicle_num: str) -> bool:
        ...


class ZoneAvailabilityRepositoryProtocol(Protocol):
    def get_counts_by_slot_type(self, *, slot_type: str) -> list[Any]:
        ...
