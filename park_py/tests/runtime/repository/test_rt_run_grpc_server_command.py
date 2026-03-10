from __future__ import annotations

from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import SimpleTestCase


class RunGrpcServerCommandRuntimeTests(SimpleTestCase):
    def test_should_bind_and_start_registered_server__when_command_runs(self) -> None:
        """[RT-RUNTIME-01] run_grpc_server 명령 실행"""

        fake_server = Mock()
        fake_server.add_insecure_port.return_value = 50051
        stdout = StringIO()

        with patch("park_py.grpc_runtime.resolve_grpc_runtime") as resolve_runtime:
            runtime = Mock()
            runtime.service_name = "vehicle"
            runtime.default_host = "0.0.0.0"
            runtime.default_port = 50051
            runtime.host_env = "VEHICLE_GRPC_HOST"
            runtime.port_env = "VEHICLE_GRPC_PORT"
            runtime.build_server.return_value = fake_server
            resolve_runtime.return_value = runtime

            with self.assertRaises(SystemExit):
                call_command(
                    "run_grpc_server",
                    "--service",
                    "vehicle",
                    stdout=stdout,
                )

        fake_server.add_insecure_port.assert_called_once_with("0.0.0.0:50051")
        fake_server.start.assert_called_once()
        fake_server.wait_for_termination.assert_called_once()
