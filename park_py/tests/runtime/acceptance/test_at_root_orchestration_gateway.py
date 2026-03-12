from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings

from park_py.tests.orchestration_service.support import (
    FakeParkingCommandGateway,
    FakeParkingQueryGateway,
    FakeVehicleGateway,
    FakeZoneGateway,
)


@override_settings(ROOT_URLCONF="park_py.urls")
class RootOrchestrationGatewayAcceptanceTests(TestCase):
    def test_should_route_entry_request_through_root_urlconf__when_gateway_is_enabled(self) -> None:
        """[AT-RUNTIME-01] 기본 URL에서 orchestration gateway 노출"""

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
                HTTP_IDEMPOTENCY_KEY="runtime-entry-idem-001",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "COMPLETED")
