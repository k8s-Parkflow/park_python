from __future__ import annotations

from io import StringIO
from unittest.mock import call, patch

from django.core.management import call_command
from django.test import SimpleTestCase


class ServiceDatabaseMigrationCommandRuntimeTests(SimpleTestCase):
    def test_should_run_target_database_migration__when_service_database_command_runs(self) -> None:
        stdout = StringIO()

        with patch("django.core.management.call_command") as delegated_call:
            call_command(
                "migrate_service_db",
                "--service",
                "parking_command",
                "--verbosity",
                "2",
                stdout=stdout,
            )

        delegated_call.assert_called_once()
        self.assertEqual(delegated_call.call_args.args, ("migrate",))
        self.assertEqual(
            delegated_call.call_args.kwargs,
            {
                "database": "parking_command",
                "interactive": False,
                "verbosity": 2,
                "stdout": delegated_call.call_args.kwargs["stdout"],
            },
        )

    def test_should_run_all_service_database_migrations_in_order__when_batch_command_runs(self) -> None:
        stdout = StringIO()

        with patch("django.core.management.call_command") as delegated_call:
            call_command(
                "migrate_msa_databases",
                "--verbosity",
                "2",
                stdout=stdout,
            )

        self.assertEqual(
            delegated_call.call_args_list,
            [
                call(
                    "migrate_service_db",
                    "--service",
                    "orchestration",
                    "--verbosity",
                    "2",
                    stdout=delegated_call.call_args_list[0].kwargs["stdout"],
                ),
                call(
                    "migrate_service_db",
                    "--service",
                    "vehicle",
                    "--verbosity",
                    "2",
                    stdout=delegated_call.call_args_list[1].kwargs["stdout"],
                ),
                call(
                    "migrate_service_db",
                    "--service",
                    "zone",
                    "--verbosity",
                    "2",
                    stdout=delegated_call.call_args_list[2].kwargs["stdout"],
                ),
                call(
                    "migrate_service_db",
                    "--service",
                    "parking_command",
                    "--verbosity",
                    "2",
                    stdout=delegated_call.call_args_list[3].kwargs["stdout"],
                ),
                call(
                    "migrate_service_db",
                    "--service",
                    "parking_query",
                    "--verbosity",
                    "2",
                    stdout=delegated_call.call_args_list[4].kwargs["stdout"],
                ),
            ],
        )
