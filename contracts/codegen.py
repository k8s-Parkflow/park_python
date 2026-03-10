from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import grpc_tools
from grpc_tools import protoc


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTO_ROOT = REPO_ROOT / "contracts" / "proto"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "contracts" / "gen" / "python"


def iter_proto_files(proto_root: Path) -> list[Path]:
    return sorted(proto_root.rglob("*.proto"))


def build_protoc_args(proto_root: Path, output_root: Path) -> list[str]:
    proto_files = iter_proto_files(proto_root)
    builtin_proto_root = Path(grpc_tools.__file__).resolve().parent / "_proto"
    return [
        "grpc_tools.protoc",
        f"-I{proto_root}",
        f"-I{builtin_proto_root}",
        f"--python_out={output_root}",
        f"--grpc_python_out={output_root}",
        *[str(proto_file) for proto_file in proto_files],
    ]


def generate_python(
    *,
    proto_root: Optional[Path] = None,
    output_root: Optional[Path] = None,
) -> int:
    resolved_proto_root = proto_root or DEFAULT_PROTO_ROOT
    resolved_output_root = output_root or DEFAULT_OUTPUT_ROOT
    resolved_output_root.mkdir(parents=True, exist_ok=True)
    return protoc.main(build_protoc_args(resolved_proto_root, resolved_output_root))


def ensure_python_packages(output_root: Path) -> None:
    for directory in [output_root, *output_root.rglob("*")]:
        if directory.is_dir():
            init_file = directory / "__init__.py"
            if not init_file.exists():
                init_file.write_text("", encoding="utf-8")


def generate_and_prepare(
    *,
    proto_root: Optional[Path] = None,
    output_root: Optional[Path] = None,
) -> int:
    resolved_proto_root = proto_root or DEFAULT_PROTO_ROOT
    resolved_output_root = output_root or DEFAULT_OUTPUT_ROOT
    result = generate_python(proto_root=resolved_proto_root, output_root=resolved_output_root)
    if result == 0:
        ensure_python_packages(resolved_output_root)
    return result
