from __future__ import annotations

import os
from importlib import import_module
from unittest import TestCase
from unittest.mock import patch


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

    def test_should_setup_django_and_delegate_to_serve__when_run_from_cli_runs(self) -> None:
        cases = [
            ("vehicle_service.grpc_runtime", "vehicle_service.settings"),
            ("zone_service.grpc_runtime", "zone_service.settings"),
            ("parking_command_service.grpc_runtime", "parking_command_service.settings"),
            ("parking_query_service.grpc_runtime", "parking_query_service.settings"),
        ]

        for module_path, settings_module in cases:
            with self.subTest(module=module_path):
                module = import_module(module_path)
                with patch.dict(os.environ, {}, clear=True):
                    with patch(f"{module_path}.django.setup") as django_setup:
                        with patch(f"{module_path}.serve") as serve:
                            module.run_from_cli(host="127.0.0.1", port=65000, stdout="stdout")

                            self.assertEqual(os.environ["DJANGO_SETTINGS_MODULE"], settings_module)

                django_setup.assert_called_once_with()
                serve.assert_called_once_with(host="127.0.0.1", port=65000, stdout="stdout")
