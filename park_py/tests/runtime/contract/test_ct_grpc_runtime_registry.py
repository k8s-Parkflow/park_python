from __future__ import annotations

from unittest import TestCase

from park_py.grpc_runtime import resolve_grpc_runtime


class GrpcRuntimeRegistryContractTests(TestCase):
    def test_should_resolve_registered_service_runtime__when_service_name_is_known(self) -> None:
        """[CT-RUNTIME-01] gRPC 런타임 registry 계약"""

        runtime = resolve_grpc_runtime("parking_query")

        self.assertEqual(runtime.service_name, "parking_query")
        self.assertEqual(runtime.port_env, "PARKING_QUERY_GRPC_PORT")
        self.assertEqual(runtime.default_port, 50054)

