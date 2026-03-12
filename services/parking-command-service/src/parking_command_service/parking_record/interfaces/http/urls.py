from django.urls import path

from parking_command_service.parking_record.interfaces.http.internal_views import (
    cancel_parking_entry,
    create_parking_entry,
    create_parking_exit,
    restore_parking_exit,
)
from parking_command_service.parking_record.interfaces.http.public_views import (
    ParkingEntryView,
    ParkingExitView,
)

urlpatterns = [
    path("api/parking/entry", ParkingEntryView.as_view(), name="parking-entry"),
    path("api/parking/exit", ParkingExitView.as_view(), name="parking-exit"),
    path("internal/parking-command/entries", create_parking_entry),
    path("internal/parking-command/entries/compensations", cancel_parking_entry),
    path("internal/parking-command/exits", create_parking_exit),
    path("internal/parking-command/exits/compensations", restore_parking_exit),
]
