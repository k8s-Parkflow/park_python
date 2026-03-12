from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class ServiceGrpcEntrypointCommandRuntimeTests(SimpleTestCase):
    def test_should_call_local_service_runtime__when_service_command_runs(self) -> None:
        stdout = StringIO()
        cases = [
            ("run_vehicle_grpc", "vehicle_service.grpc_runtime.serve"),
            ("run_zone_grpc", "zone_service.grpc_runtime.serve"),
            ("run_parking_command_grpc", "parking_command_service.grpc_runtime.serve"),
            ("run_parking_query_grpc", "parking_query_service.grpc_runtime.serve"),
        ]

        for command_name, runtime_path in cases:
            with self.subTest(command=command_name):
                with patch(runtime_path) as serve:
                    call_command(
                        command_name,
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "65000",
                        stdout=stdout,
                    )

                serve.assert_called_once()
                kwargs = serve.call_args.kwargs
                self.assertEqual(kwargs["host"], "127.0.0.1")
                self.assertEqual(kwargs["port"], 65000)
                self.assertIn("stdout", kwargs)
