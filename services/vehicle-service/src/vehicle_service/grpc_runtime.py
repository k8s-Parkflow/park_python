from __future__ import annotations

import os

import django

from vehicle_service.vehicle.interfaces.grpc.server import build_vehicle_grpc_server


SERVICE_NAME = "vehicle"
HOST_ENV = "VEHICLE_GRPC_HOST"
PORT_ENV = "VEHICLE_GRPC_PORT"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 50051
DEFAULT_SETTINGS_MODULE = "vehicle_service.settings"


def build_bind_target(*, host: str, port: int) -> str:
    return f"{host}:{port}"


def resolve_bind_target(*, host: str | None = None, port: int | None = None) -> str:
    resolved_host = host or os.getenv(HOST_ENV, DEFAULT_HOST)
    resolved_port = port or int(os.getenv(PORT_ENV, str(DEFAULT_PORT)))
    return build_bind_target(host=resolved_host, port=resolved_port)


def serve(*, host: str | None = None, port: int | None = None, stdout=None) -> None:
    server = build_vehicle_grpc_server()
    bind_target = resolve_bind_target(host=host, port=port)
    bound_port = server.add_insecure_port(bind_target)
    if bound_port <= 0:
        raise RuntimeError(f"failed to bind grpc server: {bind_target}")

    if stdout is not None:
        stdout.write(f"starting grpc service {SERVICE_NAME} on {bind_target}")

    server.start()
    server.wait_for_termination()


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
    django.setup()
    serve()


if __name__ == "__main__":
    main()
