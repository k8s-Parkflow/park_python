from __future__ import annotations

import unittest
from pathlib import Path

from contracts.codegen import build_protoc_args


class ProtocArgumentBuilderUnitTests(unittest.TestCase):
    def test_should_include_all_proto_files__when_building_python_codegen_arguments(self) -> None:
        # Given
        proto_root = Path(__file__).resolve().parents[2] / "proto"
        output_root = Path("/tmp/contracts-gen")

        # When
        args = build_protoc_args(proto_root, output_root)

        # Then
        self.assertIn(f"-I{proto_root}", args)
        self.assertIn(f"--python_out={output_root}", args)
        self.assertIn(f"--grpc_python_out={output_root}", args)
        self.assertTrue(any(arg.endswith("vehicle/v1/vehicle.proto") for arg in args))
        self.assertTrue(any(arg.endswith("zone/v1/zone.proto") for arg in args))
        self.assertTrue(any(arg.endswith("orchestration/v1/orchestration.proto") for arg in args))
