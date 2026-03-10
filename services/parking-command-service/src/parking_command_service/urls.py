from django.urls import path

from parking_command_service.views import cancel_parking_entry
from parking_command_service.views import create_parking_entry
from parking_command_service.views import create_parking_exit
from parking_command_service.views import restore_parking_exit


urlpatterns = [
    path("internal/parking-command/entries", create_parking_entry),
    path("internal/parking-command/entries/compensations", cancel_parking_entry),
    path("internal/parking-command/exits", create_parking_exit),
    path("internal/parking-command/exits/compensations", restore_parking_exit),
]

