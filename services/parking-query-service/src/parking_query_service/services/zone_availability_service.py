from typing import Any, Optional

from parking_query_service.parking_view.application.use_cases.get_zone_availability import (
    ZoneAvailabilityService as _ZoneAvailabilityService,
)
from parking_query_service.repositories import ZoneAvailabilityRepository


class ZoneAvailabilityService(_ZoneAvailabilityService):
    def __init__(
        self,
        *,
        zone_availability_repository: Optional[Any] = None,
    ) -> None:
        super().__init__(
            zone_availability_repository=zone_availability_repository
            or ZoneAvailabilityRepository(),
        )


__all__ = ["ZoneAvailabilityService"]
