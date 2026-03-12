from django.urls import path

from parking_query_service.views import get_current_location
from parking_query_service.views import get_current_parking_view
from parking_query_service.views import get_zone_slots
from parking_query_service.views import project_parking_entry
from parking_query_service.views import project_parking_exit
from parking_query_service.views import restore_parking_exit_projection
from parking_query_service.views import revert_parking_entry_projection


urlpatterns = [
    path("zones/<int:zone_id>/slots", get_zone_slots),
    path("api/parking/current/<str:vehicle_num>", get_current_location),
    path("internal/parking-query/current-parking/<str:vehicle_num>", get_current_parking_view),
    path("internal/parking-query/entries", project_parking_entry),
    path("internal/parking-query/entries/compensations", revert_parking_entry_projection),
    path("internal/parking-query/exits", project_parking_exit),
    path("internal/parking-query/exits/compensations", restore_parking_exit_projection),
]
