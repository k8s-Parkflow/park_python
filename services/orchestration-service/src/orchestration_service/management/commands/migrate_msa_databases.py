from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand

from park_py.service_databases import SERVICE_MIGRATION_ORDER


class Command(BaseCommand):
    help = "Run Django migrations for all service databases in MSA order."

    def handle(self, *args, **options):
        for service_name in SERVICE_MIGRATION_ORDER:
            call_command(
                "migrate_service_db",
                "--service",
                service_name,
                "--verbosity",
                str(options["verbosity"]),
                stdout=self.stdout,
            )
