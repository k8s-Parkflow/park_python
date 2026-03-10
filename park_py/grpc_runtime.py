from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

from parking_command_service.grpc.server import build_parking_command_grpc_server
from parking_query_service.grpc.server import build_parking_query_grpc_server
from vehicle_service.grpc.server import build_vehicle_grpc_server
from zone_service.grpc.server import build_zone_grpc_server


@dataclass(frozen=True)
class GrpcServiceRuntime:
    service_name: str
    build_server: Callable
    host_env: str
    port_env: str
    default_host: str
    default_port: int


RUNTIMES = {
    "vehicle": GrpcServiceRuntime(
        service_name="vehicle",
        build_server=build_vehicle_grpc_server,
        host_env="VEHICLE_GRPC_HOST",
        port_env="VEHICLE_GRPC_PORT",
        default_host="0.0.0.0",
        default_port=50051,
    ),
    "zone": GrpcServiceRuntime(
        service_name="zone",
        build_server=build_zone_grpc_server,
        host_env="ZONE_GRPC_HOST",
        port_env="ZONE_GRPC_PORT",
        default_host="0.0.0.0",
        default_port=50052,
    ),
    "parking_command": GrpcServiceRuntime(
        service_name="parking_command",
        build_server=build_parking_command_grpc_server,
        host_env="PARKING_COMMAND_GRPC_HOST",
        port_env="PARKING_COMMAND_GRPC_PORT",
        default_host="0.0.0.0",
        default_port=50053,
    ),
    "parking_query": GrpcServiceRuntime(
        service_name="parking_query",
        build_server=build_parking_query_grpc_server,
        host_env="PARKING_QUERY_GRPC_HOST",
        port_env="PARKING_QUERY_GRPC_PORT",
        default_host="0.0.0.0",
        default_port=50054,
    ),
}


def resolve_grpc_runtime(service_name: str) -> GrpcServiceRuntime:
    if service_name not in RUNTIMES:
        raise KeyError(f"unsupported grpc service: {service_name}")
    return RUNTIMES[service_name]


def build_bind_target(*, host: str, port: int) -> str:
    return f"{host}:{port}"


def resolve_bind_target(*, runtime: GrpcServiceRuntime, host: str | None, port: int | None) -> str:
    resolved_host = host or os.getenv(runtime.host_env, runtime.default_host)
    resolved_port = port or int(os.getenv(runtime.port_env, str(runtime.default_port)))
    return build_bind_target(host=resolved_host, port=resolved_port)
