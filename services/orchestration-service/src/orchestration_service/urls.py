from django.urls import path

from orchestration_service.views import create_entry, create_exit, get_saga_operation


urlpatterns = [
    path("api/v1/parking/entries", create_entry),
    path("api/v1/parking/exits", create_exit),
    path("api/v1/saga-operations/<str:operation_id>", get_saga_operation),
]
