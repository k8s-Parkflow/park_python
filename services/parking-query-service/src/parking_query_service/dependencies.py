from parking_query_service.parking_view.bootstrap import build_get_current_location
from parking_query_service.parking_view.application.use_cases.get_current_location import (
    CurrentLocationService,
)


def build_current_location_service() -> CurrentLocationService:
    return build_get_current_location()
