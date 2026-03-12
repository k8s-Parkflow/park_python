from django.urls import path

from parking_query_service.parking_view.interfaces.http.views import (
    get_current_location,
    get_current_parking_view,
    get_zone_slots,
    project_parking_entry,
    project_parking_exit,
    restore_parking_exit_projection,
    revert_parking_entry_projection,
)


urlpatterns = [
    path("zones/<int:zone_id>/slots", get_zone_slots),
    path("api/parking/current/<str:vehicle_num>", get_current_location),
    path("internal/parking-query/current-parking/<str:vehicle_num>", get_current_parking_view),
    path("internal/parking-query/entries", project_parking_entry),
    path("internal/parking-query/entries/compensations", revert_parking_entry_projection),
    path("internal/parking-query/exits", project_parking_exit),
    path("internal/parking-query/exits/compensations", restore_parking_exit_projection),
]
