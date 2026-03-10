from __future__ import annotations

import unittest

from contracts.tests.support import GeneratedProtoModules


class ProtoContractShapeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generated = GeneratedProtoModules()

    def tearDown(self) -> None:
        self.generated.cleanup()

    def test_should_match_vehicle_get_contract__when_generated_module_is_loaded(self) -> None:
        # Given
        vehicle_pb2 = self.generated.import_module("vehicle.v1.vehicle_pb2")

        # When
        request_fields = list(vehicle_pb2.GetVehicleRequest.DESCRIPTOR.fields_by_name.keys())
        response_fields = list(vehicle_pb2.GetVehicleResponse.DESCRIPTOR.fields_by_name.keys())

        # Then
        self.assertEqual(request_fields, ["vehicle_num"])
        self.assertEqual(response_fields, ["vehicle_num", "vehicle_type", "active"])

    def test_should_match_parking_command_create_entry_contract__when_generated_module_is_loaded(
        self,
    ) -> None:
        # Given
        parking_command_pb2 = self.generated.import_module(
            "parking_command.v1.parking_command_pb2"
        )

        # When
        request_fields = list(
            parking_command_pb2.CreateEntryRequest.DESCRIPTOR.fields_by_name.keys()
        )
        response_fields = list(
            parking_command_pb2.CreateEntryResponse.DESCRIPTOR.fields_by_name.keys()
        )

        # Then
        self.assertEqual(
            request_fields,
            [
                "context",
                "operation_id",
                "vehicle_num",
                "slot_id",
                "zone_id",
                "slot_code",
                "slot_type",
            ],
        )
        self.assertEqual(
            response_fields,
            ["history_id", "slot_id", "vehicle_num", "entry_at", "status", "slot_code"],
        )

    def test_should_match_parking_query_projection_contract__when_generated_module_is_loaded(
        self,
    ) -> None:
        # Given
        parking_query_pb2 = self.generated.import_module("parking_query.v1.parking_query_pb2")

        # When
        apply_entry_fields = list(
            parking_query_pb2.ApplyEntryProjectionRequest.DESCRIPTOR.fields_by_name.keys()
        )
        current_parking_fields = list(
            parking_query_pb2.GetCurrentParkingResponse.DESCRIPTOR.fields_by_name.keys()
        )

        # Then
        self.assertEqual(
            apply_entry_fields,
            [
                "context",
                "operation_id",
                "history_id",
                "vehicle_num",
                "slot_id",
                "zone_id",
                "slot_type",
                "entry_at",
                "slot_code",
                "zone_name",
            ],
        )
        self.assertEqual(
            current_parking_fields,
            [
                "vehicle_num",
                "slot_id",
                "zone_id",
                "slot_type",
                "entry_at",
                "updated_at",
                "slot_code",
                "zone_name",
            ],
        )

    def test_should_match_zone_validate_entry_policy_contract__when_generated_module_is_loaded(
        self,
    ) -> None:
        # Given
        zone_pb2 = self.generated.import_module("zone.v1.zone_pb2")

        # When
        response_fields = list(
            zone_pb2.ValidateEntryPolicyResponse.DESCRIPTOR.fields_by_name.keys()
        )

        # Then
        self.assertEqual(
            response_fields,
            [
                "slot_id",
                "zone_id",
                "slot_type",
                "zone_active",
                "entry_allowed",
                "zone_name",
                "slot_code",
            ],
        )
