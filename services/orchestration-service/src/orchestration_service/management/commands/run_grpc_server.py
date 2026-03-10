from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from park_py.grpc_runtime import resolve_bind_target, resolve_grpc_runtime


class Command(BaseCommand):
    help = "Run a gRPC server for a specific internal service."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--service",
            required=True,
            choices=["vehicle", "zone", "parking_command", "parking_query"],
        )
        parser.add_argument("--host")
        parser.add_argument("--port", type=int)

    def handle(self, *args, **options):
        try:
            runtime = resolve_grpc_runtime(options["service"])
        except KeyError as error:
            raise CommandError(str(error)) from error

        server = runtime.build_server()
        bind_target = resolve_bind_target(
            runtime=runtime,
            host=options.get("host"),
            port=options.get("port"),
        )
        bound_port = server.add_insecure_port(bind_target)
        if bound_port <= 0:
            raise CommandError(f"failed to bind grpc server: {bind_target}")

        self.stdout.write(f"starting grpc service {runtime.service_name} on {bind_target}")
        server.start()
        try:
            server.wait_for_termination()
        finally:
            raise SystemExit(0)
