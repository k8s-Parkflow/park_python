from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class ServiceGrpcEntrypointCommandRuntimeTests(SimpleTestCase):
    def test_should_delegate_to_common_grpc_runner__when_service_wrapper_runs(self) -> None:
        stdout = StringIO()
        cases = [
            ("run_vehicle_grpc", "vehicle"),
            ("run_zone_grpc", "zone"),
            ("run_parking_command_grpc", "parking_command"),
            ("run_parking_query_grpc", "parking_query"),
        ]

        for command_name, service_name in cases:
            with self.subTest(command=command_name):
                with patch("django.core.management.call_command") as delegated_call:
                    call_command(
                        command_name,
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "65000",
                        stdout=stdout,
                    )

                delegated_call.assert_called_once()
                args = delegated_call.call_args.args
                kwargs = delegated_call.call_args.kwargs
                self.assertEqual(
                    args,
                    (
                        "run_grpc_server",
                        "--service",
                        service_name,
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "65000",
                    ),
                )
                self.assertIn("stdout", kwargs)
