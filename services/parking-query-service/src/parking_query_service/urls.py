from django.urls import path

from parking_query_service.views import get_current_location


urlpatterns = [
    path("api/parking/current/<str:vehicle_num>", get_current_location),
]
