from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the zone-service gRPC server."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--host")
        parser.add_argument("--port", type=int)

    def handle(self, *args, **options):
        command_args = ["run_grpc_server", "--service", "zone"]
        if options.get("host"):
            command_args.extend(["--host", options["host"]])
        if options.get("port") is not None:
            command_args.extend(["--port", str(options["port"])])
        call_command(*command_args, stdout=self.stdout)
