import sys
from pathlib import Path

from django.test import SimpleTestCase


ORCHESTRATION_SERVICE_SRC = Path(__file__).resolve().parents[2] / "src"
if str(ORCHESTRATION_SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(ORCHESTRATION_SERVICE_SRC))


class OrchestrationDependencyClientContractTests(SimpleTestCase):
    def test_should_parse_vehicle_lookup_response__when_vehicle_contract_matches(
        self,
    ) -> None:
        """[CT-OR-CLIENT-01] vehicle-service 클라이언트 계약"""

        from orchestration_service.clients.vehicle import VehicleServiceClient

        # Given
        payload = {
            "vehicle_num": "12가3456",
            "vehicle_type": "GENERAL",
        }

        # When
        result = VehicleServiceClient().parse_lookup_response(payload)

        # Then
        self.assertEqual(
            result,
            {
                "vehicle_num": "12가3456",
                "vehicle_type": "GENERAL",
            },
        )

    def test_should_parse_zone_policy_response__when_zone_contract_matches(self) -> None:
        """[CT-OR-CLIENT-02] zone-service 클라이언트 계약"""

        from orchestration_service.clients.zone import ZoneServiceClient

        # Given
        payload = {
            "slot_id": 7,
            "zone_id": 1,
            "slot_type": "GENERAL",
            "zone_active": True,
            "entry_allowed": True,
        }

        # When
        result = ZoneServiceClient().parse_entry_policy_response(payload)

        # Then
        self.assertEqual(
            result,
            {
                "slot_id": 7,
                "zone_id": 1,
                "slot_type": "GENERAL",
                "zone_active": True,
                "entry_allowed": True,
            },
        )

    def test_should_parse_parking_command_entry_response__when_command_contract_matches(
        self,
    ) -> None:
        """[CT-OR-CLIENT-03] parking-command-service 클라이언트 계약"""

        from orchestration_service.clients.parking_command import ParkingCommandServiceClient

        # Given
        payload = {
            "history_id": 101,
            "slot_id": 7,
            "vehicle_num": "12가3456",
            "entry_at": "2026-03-10T10:00:00+09:00",
            "status": "PARKED",
        }

        # When
        result = ParkingCommandServiceClient().parse_entry_response(payload)

        # Then
        self.assertEqual(
            result,
            {
                "history_id": 101,
                "slot_id": 7,
                "vehicle_num": "12가3456",
                "entry_at": "2026-03-10T10:00:00+09:00",
                "status": "PARKED",
            },
        )

    def test_should_parse_query_projection_response__when_projection_contract_matches(
        self,
    ) -> None:
        """[CT-OR-CLIENT-04] parking-query-service 클라이언트 계약"""

        from orchestration_service.clients.parking_query import ParkingQueryServiceClient

        # Given
        payload = {
            "projected": True,
            "updated_at": "2026-03-10T10:00:01+09:00",
        }

        # When
        result = ParkingQueryServiceClient().parse_projection_response(payload)

        # Then
        self.assertEqual(
            result,
            {
                "projected": True,
                "updated_at": "2026-03-10T10:00:01+09:00",
            },
        )
