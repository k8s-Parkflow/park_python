from django.urls import path

from vehicle_service.views import get_vehicle


urlpatterns = [
    path("internal/vehicles/<str:vehicle_num>", get_vehicle),
]

