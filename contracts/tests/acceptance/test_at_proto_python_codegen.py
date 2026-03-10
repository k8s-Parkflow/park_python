from __future__ import annotations

import unittest

from contracts.tests.support import GeneratedProtoModules


class ProtoPythonCodegenAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generated = GeneratedProtoModules()

    def tearDown(self) -> None:
        self.generated.cleanup()

    def test_should_generate_all_service_modules__when_python_codegen_runs(self) -> None:
        # Given / When
        module_names = [
            "common.v1.common_pb2",
            "common.v1.errors_pb2",
            "vehicle.v1.vehicle_pb2",
            "vehicle.v1.vehicle_pb2_grpc",
            "zone.v1.zone_pb2",
            "zone.v1.zone_pb2_grpc",
            "parking_command.v1.parking_command_pb2",
            "parking_command.v1.parking_command_pb2_grpc",
            "parking_query.v1.parking_query_pb2",
            "parking_query.v1.parking_query_pb2_grpc",
            "orchestration.v1.orchestration_pb2",
            "orchestration.v1.orchestration_pb2_grpc",
        ]

        # Then
        for module_name in module_names:
            with self.subTest(module_name=module_name):
                module = self.generated.import_module(module_name)
                self.assertIsNotNone(module)
