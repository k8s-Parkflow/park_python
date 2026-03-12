from __future__ import annotations

import sys
from pathlib import Path


SERVICE_SRC_RELATIVE_PATHS = (
    Path("services/orchestration-service/src"),
    Path("services/vehicle-service/src"),
    Path("services/zone-service/src"),
    Path("services/parking-command-service/src"),
    Path("services/parking-query-service/src"),
)


def ensure_on_sys_path(*paths: Path) -> None:
    for path in reversed(paths):
        resolved_path = str(path.resolve())
        if resolved_path not in sys.path:
            sys.path.insert(0, resolved_path)


def bootstrap_service_runtime(anchor_file: str) -> Path:
    anchor_path = Path(anchor_file).resolve()
    repo_root = anchor_path.parents[4]
    service_src = anchor_path.parents[1]
    package_dir = anchor_path.parent
    package_dir_path = str(package_dir)
    while package_dir_path in sys.path:
        sys.path.remove(package_dir_path)
    ensure_on_sys_path(repo_root, service_src)
    return repo_root


def bootstrap_repo_services(anchor_file: str) -> Path:
    repo_root = Path(anchor_file).resolve().parent
    service_src_paths = tuple(repo_root / relative_path for relative_path in SERVICE_SRC_RELATIVE_PATHS)
    ensure_on_sys_path(repo_root, *service_src_paths)
    return repo_root
