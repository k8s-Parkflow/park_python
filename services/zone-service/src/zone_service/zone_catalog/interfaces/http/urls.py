from django.urls import path

from zone_service.zone_catalog.interfaces.http.views import get_entry_policy

urlpatterns = [
    path("internal/zones/slots/<int:slot_id>/entry-policy", get_entry_policy),
]
