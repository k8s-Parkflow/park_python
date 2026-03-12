from __future__ import annotations

from importlib import import_module
from unittest import TestCase


class ServiceGrpcRuntimeUnitTests(TestCase):
    def test_should_build_bind_target__when_host_and_port_are_given(self) -> None:
        cases = [
            "vehicle_service.grpc_runtime",
            "zone_service.grpc_runtime",
            "parking_command_service.grpc_runtime",
            "parking_query_service.grpc_runtime",
        ]

        for module_path in cases:
            with self.subTest(module=module_path):
                module = import_module(module_path)
                self.assertEqual(
                    module.build_bind_target(host="0.0.0.0", port=65000),
                    "0.0.0.0:65000",
                )
