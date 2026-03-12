from django.urls import path

from vehicle_service.vehicle.interfaces.http.views import get_vehicle


urlpatterns = [
    path("internal/vehicles/<str:vehicle_num>", get_vehicle),
]
