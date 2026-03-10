from django.urls import path

from orchestration_service.views import create_parking_entry
from orchestration_service.views import create_parking_exit
from orchestration_service.views import get_saga_operation_status


urlpatterns = [
    path("api/v1/parking/entries", create_parking_entry),
    path("api/v1/parking/exits", create_parking_exit),
    path("api/v1/saga-operations/<str:operation_id>", get_saga_operation_status),
]

