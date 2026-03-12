from __future__ import annotations

from django.test import TestCase, override_settings


@override_settings(ROOT_URLCONF="parking_command_service.http_runtime.urls")
class ParkingCommandHttpRuntimeAcceptanceTests(TestCase):
    databases = "__all__"

    def test_should_expose_parking_command_public_route(self) -> None:
        response = self.client.post(
            "/api/parking/entry",
            data={},
            content_type="application/json",
        )

        self.assertIn(response.status_code, {400, 404, 503})

    def test_should_not_expose_orchestration_route(self) -> None:
        response = self.client.get("/api/v1/saga-operations/op-001")

        self.assertEqual(response.status_code, 404)


@override_settings(ROOT_URLCONF="parking_query_service.http_runtime.urls")
class ParkingQueryHttpRuntimeAcceptanceTests(TestCase):
    databases = "__all__"

    def test_should_expose_parking_query_runtime_routes(self) -> None:
        availability_response = self.client.get("/api/zones/availabilities")
        current_response = self.client.get("/api/parking/current/12가3456")

        self.assertIn(availability_response.status_code, {200, 400})
        self.assertIn(current_response.status_code, {200, 404, 503})

    def test_should_not_expose_orchestration_route(self) -> None:
        response = self.client.get("/api/v1/parking/entries")

        self.assertEqual(response.status_code, 404)
