from django.urls import include, path

from park_py.error_handling import handler404 as json_handler404
from park_py.error_handling import handler500 as json_handler500
from parking_query_service.parking_view.interfaces.http.views import availability


urlpatterns = [
    path("api/zones/availabilities", availability),
    path("", include("parking_query_service.urls")),
]

handler404 = json_handler404
handler500 = json_handler500
