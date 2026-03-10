from __future__ import annotations

import unittest

from contracts.tests.support import GeneratedProtoModules


class GeneratedOutputLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generated = GeneratedProtoModules()

    def tearDown(self) -> None:
        self.generated.cleanup()

    def test_should_persist_package_layout__when_codegen_completes(self) -> None:
        # Given / When
        expected_paths = [
            self.generated.output_root / "common" / "v1" / "common_pb2.py",
            self.generated.output_root / "vehicle" / "v1" / "vehicle_pb2.py",
            self.generated.output_root / "zone" / "v1" / "zone_pb2_grpc.py",
            self.generated.output_root / "parking_command" / "v1" / "parking_command_pb2.py",
            self.generated.output_root / "parking_query" / "v1" / "parking_query_pb2_grpc.py",
            self.generated.output_root / "orchestration" / "v1" / "orchestration_pb2.py",
        ]

        # Then
        for expected_path in expected_paths:
            with self.subTest(expected_path=str(expected_path)):
                self.assertTrue(expected_path.exists())
