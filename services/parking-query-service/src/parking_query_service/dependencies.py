from parking_query_service.parking_view.bootstrap import build_get_current_location
from parking_query_service.parking_view.bootstrap import build_zone_slot_query_service


def build_current_location_service():
    return build_get_current_location()
