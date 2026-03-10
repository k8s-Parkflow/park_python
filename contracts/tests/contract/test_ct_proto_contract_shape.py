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
            ["context", "operation_id", "vehicle_num", "slot_id"],
        )
        self.assertEqual(
            response_fields,
            ["history_id", "slot_id", "vehicle_num", "entry_at", "status"],
        )
