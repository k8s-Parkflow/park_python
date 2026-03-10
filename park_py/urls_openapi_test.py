from django.urls import include, path

from park_py.error_handling import handler404 as json_handler404
from park_py.error_handling import handler500 as json_handler500
from park_py.openapi import openapi_json_view, swagger_ui_view

urlpatterns = [
    path("api/docs/openapi.json", openapi_json_view, name="openapi-json"),
    path("api/docs/swagger", swagger_ui_view, name="swagger-ui"),
    path("", include("parking_command_service.urls")),
]

handler404 = json_handler404
handler500 = json_handler500
