from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from shared.service_databases import SERVICE_TO_DB_ALIAS


class Command(BaseCommand):
    help = "Run Django migrations for a single MSA service database."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--service", required=True, choices=sorted(SERVICE_TO_DB_ALIAS))

    def handle(self, *args, **options):
        service_name = options["service"]
        if service_name not in SERVICE_TO_DB_ALIAS:
            raise CommandError(f"unsupported service database: {service_name}")
        call_command(
            "migrate",
            database=SERVICE_TO_DB_ALIAS[service_name],
            interactive=False,
            verbosity=options["verbosity"],
            stdout=self.stdout,
        )
