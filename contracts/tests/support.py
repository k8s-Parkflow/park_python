from __future__ import annotations

import importlib
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType

from contracts.codegen import generate_and_prepare


class GeneratedProtoModules:
    def __init__(self) -> None:
        self._temp_dir = TemporaryDirectory()
        self.output_root = Path(self._temp_dir.name)
        self.proto_root = Path(__file__).resolve().parents[1] / "proto"
        result = generate_and_prepare(proto_root=self.proto_root, output_root=self.output_root)
        if result != 0:
            raise AssertionError(f"proto generation failed with exit code {result}")
        sys.path.insert(0, str(self.output_root))

    def import_module(self, module_name: str) -> ModuleType:
        return importlib.import_module(module_name)

    def cleanup(self) -> None:
        output_root_str = str(self.output_root)
        if output_root_str in sys.path:
            sys.path.remove(output_root_str)
        self._temp_dir.cleanup()
