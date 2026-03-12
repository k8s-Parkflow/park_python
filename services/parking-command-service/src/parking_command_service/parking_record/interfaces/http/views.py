from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views import View

from parking_command_service.parking_record.bootstrap import (
    get_parking_record_command_service,
)
from parking_command_service.parking_record.interfaces.http.serializers import (
    parse_entry_command,
    parse_exit_command,
)


class ParkingEntryView(View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> JsonResponse:
        command = parse_entry_command(body=request.body)
        snapshot = get_parking_record_command_service().create_entry(command=command)
        return JsonResponse(snapshot.to_dict(), status=201)


class ParkingExitView(View):
    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> JsonResponse:
        command = parse_exit_command(body=request.body)
        snapshot = get_parking_record_command_service().create_exit(command=command)
        return JsonResponse(snapshot.to_dict(), status=200)
