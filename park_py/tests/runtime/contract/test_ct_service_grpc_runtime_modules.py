from __future__ import annotations

from importlib import import_module
from unittest import TestCase


class ServiceGrpcRuntimeModulesContractTests(TestCase):
    def test_should_expose_service_specific_runtime_defaults(self) -> None:
        cases = [
            ("vehicle_service.grpc_runtime", "vehicle", "VEHICLE_GRPC_PORT", 50051),
            ("zone_service.grpc_runtime", "zone", "ZONE_GRPC_PORT", 50052),
            ("parking_command_service.grpc_runtime", "parking_command", "PARKING_COMMAND_GRPC_PORT", 50053),
            ("parking_query_service.grpc_runtime", "parking_query", "PARKING_QUERY_GRPC_PORT", 50054),
        ]

        for module_path, service_name, port_env, default_port in cases:
            with self.subTest(module=module_path):
                module = import_module(module_path)
                self.assertEqual(module.SERVICE_NAME, service_name)
                self.assertEqual(module.PORT_ENV, port_env)
                self.assertEqual(module.DEFAULT_PORT, default_port)
