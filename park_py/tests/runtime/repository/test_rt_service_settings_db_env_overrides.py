from __future__ import annotations

import importlib
import os
from unittest import TestCase
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured


class ServiceSettingsDatabaseEnvOverrideRuntimeTests(TestCase):
    def test_should_require_service_db_credentials__when_settings_are_reloaded(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ORCHESTRATION_DB_USER": "or_user",
                "ORCHESTRATION_DB_PASSWORD": "or_pass",
            },
            clear=False,
        ):
            settings_module = importlib.import_module("orchestration_service.settings")

        with patch.dict(
            os.environ,
            {
                "ORCHESTRATION_DB_USER": "",
                "ORCHESTRATION_DB_PASSWORD": "",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(
                ImproperlyConfigured,
                "ORCHESTRATION_DB_USER must be set for MariaDB configuration",
            ):
                importlib.reload(settings_module)

    def test_should_apply_service_specific_db_env_overrides__when_settings_are_reloaded(self) -> None:
        cases = [
            (
                "orchestration_service.settings",
                {
                    "ORCHESTRATION_DB_NAME": "override_orchestration",
                    "ORCHESTRATION_DB_HOST": "or-db.internal",
                    "ORCHESTRATION_DB_PORT": "3308",
                    "ORCHESTRATION_DB_USER": "or_user",
                    "ORCHESTRATION_DB_PASSWORD": "or_pass",
                },
            ),
            (
                "parking_command_service.settings",
                {
                    "PARKING_COMMAND_DB_NAME": "override_parking_command",
                    "PARKING_COMMAND_DB_HOST": "pc-db.internal",
                    "PARKING_COMMAND_DB_PORT": "3309",
                    "PARKING_COMMAND_DB_USER": "pc_user",
                    "PARKING_COMMAND_DB_PASSWORD": "pc_pass",
                },
            ),
            (
                "parking_query_service.settings",
                {
                    "PARKING_QUERY_DB_NAME": "override_parking_query",
                    "PARKING_QUERY_DB_HOST": "pq-db.internal",
                    "PARKING_QUERY_DB_PORT": "3310",
                    "PARKING_QUERY_DB_USER": "pq_user",
                    "PARKING_QUERY_DB_PASSWORD": "pq_pass",
                },
            ),
            (
                "vehicle_service.settings",
                {
                    "VEHICLE_DB_NAME": "override_vehicle",
                    "VEHICLE_DB_HOST": "vehicle-db.internal",
                    "VEHICLE_DB_PORT": "3311",
                    "VEHICLE_DB_USER": "vehicle_user",
                    "VEHICLE_DB_PASSWORD": "vehicle_pass",
                },
            ),
            (
                "zone_service.settings",
                {
                    "ZONE_DB_NAME": "override_zone",
                    "ZONE_DB_HOST": "zone-db.internal",
                    "ZONE_DB_PORT": "3312",
                    "ZONE_DB_USER": "zone_user",
                    "ZONE_DB_PASSWORD": "zone_pass",
                },
            ),
        ]

        for module_name, overrides in cases:
            with self.subTest(module=module_name):
                env_prefix = self._service_prefix(module_name)
                with patch.dict(os.environ, overrides, clear=False):
                    settings_module = importlib.import_module(module_name)
                    settings_module = importlib.reload(settings_module)

                database = settings_module.DATABASES["default"]
                self.assertEqual(database["ENGINE"], "django.db.backends.mysql")
                self.assertEqual(database["NAME"], overrides[f"{env_prefix}_DB_NAME"])
                self.assertEqual(database["HOST"], overrides[f"{env_prefix}_DB_HOST"])
                self.assertEqual(database["PORT"], overrides[f"{env_prefix}_DB_PORT"])
                self.assertEqual(database["USER"], overrides[f"{env_prefix}_DB_USER"])
                self.assertEqual(
                    database["PASSWORD"],
                    overrides[f"{env_prefix}_DB_PASSWORD"],
                )

    @staticmethod
    def _service_prefix(module_name: str) -> str:
        return {
            "orchestration_service.settings": "ORCHESTRATION",
            "parking_command_service.settings": "PARKING_COMMAND",
            "parking_query_service.settings": "PARKING_QUERY",
            "vehicle_service.settings": "VEHICLE",
            "zone_service.settings": "ZONE",
        }[module_name]
