from django.urls import path

from parking_command_service.domains.parking_record.presentation.http.views import (
    ParkingEntryView,
    ParkingExitView,
)

urlpatterns = [
    path("api/parking/entry", ParkingEntryView.as_view(), name="parking-entry"),
    path("api/parking/exit", ParkingExitView.as_view(), name="parking-exit"),
]
