from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings

from park_py.tests.orchestration_service.support import (
    FakeParkingCommandGateway,
    FakeParkingQueryGateway,
    FakeVehicleGateway,
    FakeZoneGateway,
)


@override_settings(ROOT_URLCONF="orchestration_service.http_runtime.urls")
class OrchestrationHttpRuntimeAcceptanceTests(TestCase):
    def test_should_route_entry_request_through_orchestration_runtime_urlconf(self) -> None:
        vehicle_gateway = FakeVehicleGateway(call_log=[])
        zone_gateway = FakeZoneGateway(call_log=[])
        parking_command_gateway = FakeParkingCommandGateway(call_log=[])
        parking_query_gateway = FakeParkingQueryGateway(call_log=[])

        with patch(
            "orchestration_service.saga.bootstrap.build_vehicle_gateway",
            return_value=vehicle_gateway,
        ), patch(
            "orchestration_service.saga.bootstrap.build_zone_gateway",
            return_value=zone_gateway,
        ), patch(
            "orchestration_service.saga.bootstrap.build_parking_command_gateway",
            return_value=parking_command_gateway,
        ), patch(
            "orchestration_service.saga.bootstrap.build_parking_query_gateway",
            return_value=parking_query_gateway,
        ):
            response = self.client.post(
                "/api/v1/parking/entries",
                data={
                    "vehicle_num": "12가3456",
                    "slot_id": 7,
                    "requested_at": "2026-03-10T10:00:00+09:00",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="runtime-entry-idem-002",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "COMPLETED")

    def test_should_not_expose_zone_slot_http_route__when_orchestration_runtime_is_used(self) -> None:
        response = self.client.get("/zones/1/slots")

        self.assertEqual(response.status_code, 404)
