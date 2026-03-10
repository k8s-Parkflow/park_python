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
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from park_py.error_handling import handler404 as json_handler404
from park_py.error_handling import handler500 as json_handler500
from park_py.openapi import openapi_json_view, swagger_ui_view
from parking_query_service.views import availability

urlpatterns = []

if "django.contrib.admin" in settings.INSTALLED_APPS:
    urlpatterns.append(path("admin/", admin.site.urls))

urlpatterns.append(
    path("api/zones/availabilities", availability),
)
urlpatterns.append(
    path("", include("parking_query_service.urls")),
)
urlpatterns.append(
    path("", include("parking_command_service.urls")),
)
urlpatterns.append(
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
)
urlpatterns.append(
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
)
urlpatterns.append(
    path("api/docs/openapi.json", openapi_json_view, name="openapi-json"),
)
urlpatterns.append(
    path("api/docs/swagger", swagger_ui_view, name="command-swagger-ui"),
)

handler404 = json_handler404
handler500 = json_handler500
