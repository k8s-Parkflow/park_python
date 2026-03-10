from __future__ import annotations

from unittest import TestCase

from park_py.grpc_runtime import build_bind_target


class GrpcRuntimeUnitTests(TestCase):
    def test_should_build_bind_target__when_host_and_port_are_given(self) -> None:
        """[UT-RUNTIME-01] gRPC bind target 조립"""

        self.assertEqual(build_bind_target(host="0.0.0.0", port=50054), "0.0.0.0:50054")
