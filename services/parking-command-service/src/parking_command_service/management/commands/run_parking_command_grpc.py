from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from parking_command_service import grpc_runtime


class Command(BaseCommand):
    help = "Run the parking-command-service gRPC server."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--host")
        parser.add_argument("--port", type=int)

    def handle(self, *args, **options):
        try:
            grpc_runtime.run_from_cli(
                host=options.get("host"),
                port=options.get("port"),
                stdout=self.stdout,
            )
        except RuntimeError as error:
            raise CommandError(str(error)) from error
