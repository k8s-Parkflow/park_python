"""
URL configuration for park_py project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.apps import apps
from django.urls import include, path

from park_py.error_handling import handler404 as json_handler404
from park_py.error_handling import handler500 as json_handler500
from park_py.openapi import openapi_json_view
from park_py.openapi import swagger_ui_view
from park_py.swagger_views import openapi_json
from park_py.swagger_views import swagger_ui
from parking_query_service.parking_view.interfaces.http.views import availability

urlpatterns = [
    path("openapi.json", openapi_json),
    path("swagger/", swagger_ui),
    path("api/docs/openapi.json", openapi_json_view, name="openapi-json"),
    path("api/docs/swagger", swagger_ui_view, name="swagger-ui"),
    path("api/zones/availabilities", availability),
    path("", include("orchestration_service.urls")),
    path("", include("vehicle_service.urls")),
    path("", include("zone_service.urls")),
    path("", include("parking_command_service.urls")),
    path("", include("parking_query_service.urls")),
]

if apps.is_installed("django.contrib.admin"):
    urlpatterns.insert(0, path("admin/", admin.site.urls))

handler404 = json_handler404
handler500 = json_handler500
