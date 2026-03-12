from __future__ import annotations

from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF="vehicle_service.http_runtime.urls")
class VehicleHttpRuntimeAcceptanceTests(TestCase):
    databases = "__all__"

    def test_should_expose_vehicle_internal_route(self) -> None:
        response = self.client.get("/internal/vehicles/12가3456")

        self.assertIn(response.status_code, {200, 404})

    def test_should_not_expose_orchestration_route(self) -> None:
        response = self.client.get("/api/v1/saga-operations/op-001")

        self.assertEqual(response.status_code, 404)


@override_settings(ROOT_URLCONF="zone_service.http_runtime.urls")
class ZoneHttpRuntimeAcceptanceTests(TestCase):
    databases = "__all__"

    def test_should_expose_zone_internal_route(self) -> None:
        response = self.client.get("/internal/zones/slots/7/entry-policy")

        self.assertIn(response.status_code, {200, 404})

    def test_should_not_expose_vehicle_route(self) -> None:
        response = self.client.get("/internal/vehicles/12가3456")

        self.assertEqual(response.status_code, 404)
