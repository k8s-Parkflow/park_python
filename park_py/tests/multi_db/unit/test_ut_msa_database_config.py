from __future__ import annotations

import os
from unittest import TestCase
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured

from park_py.database_config import build_service_mariadb_databases


class MsaDatabaseConfigUnitTests(TestCase):
    def test_should_require_db_credentials__when_defaults_are_missing(self) -> None:
        """[UT-MSA-DB-01] MariaDB 계정 환경변수 필수"""

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                ImproperlyConfigured,
                "ORCHESTRATION_DB_USER must be set for MariaDB configuration",
            ):
                build_service_mariadb_databases()

    def test_should_build_service_database_configs__when_required_envs_are_provided(self) -> None:
        """[UT-MSA-DB-02] 필수 MariaDB 연결 환경변수 반영"""

        with patch.dict(os.environ, self._all_service_credentials(), clear=True):
            databases = build_service_mariadb_databases()

        self.assertEqual(databases["vehicle"]["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(databases["vehicle"]["NAME"], "autoe_vehicle")
        self.assertEqual(databases["vehicle"]["HOST"], "127.0.0.1")
        self.assertEqual(databases["vehicle"]["PORT"], "3306")
        self.assertEqual(databases["vehicle"]["USER"], "vehicle_app")
        self.assertEqual(databases["vehicle"]["PASSWORD"], "vehicle_secret")
        self.assertEqual(databases["vehicle"]["OPTIONS"], {"charset": "utf8mb4"})
        self.assertEqual(databases["parking_query"]["NAME"], "autoe_parking_query")

    def test_should_apply_env_override__when_database_connection_is_provided(self) -> None:
        """[UT-MSA-DB-03] 환경변수 MariaDB 연결 override"""

        overrides = {
            **self._all_service_credentials(),
            "VEHICLE_DB_NAME": "vehicle_prod",
            "VEHICLE_DB_HOST": "mariadb.internal",
            "VEHICLE_DB_PORT": "3307",
            "VEHICLE_DB_USER": "vehicle_app",
            "VEHICLE_DB_PASSWORD": "secret",
        }
        with patch.dict(os.environ, overrides, clear=False):
            databases = build_service_mariadb_databases()

        self.assertEqual(databases["vehicle"]["NAME"], "vehicle_prod")
        self.assertEqual(databases["vehicle"]["HOST"], "mariadb.internal")
        self.assertEqual(databases["vehicle"]["PORT"], "3307")
        self.assertEqual(databases["vehicle"]["USER"], "vehicle_app")
        self.assertEqual(databases["vehicle"]["PASSWORD"], "secret")

    @staticmethod
    def _all_service_credentials() -> dict[str, str]:
        return {
            "ORCHESTRATION_DB_USER": "orchestration_app",
            "ORCHESTRATION_DB_PASSWORD": "orchestration_secret",
            "VEHICLE_DB_USER": "vehicle_app",
            "VEHICLE_DB_PASSWORD": "vehicle_secret",
            "ZONE_DB_USER": "zone_app",
            "ZONE_DB_PASSWORD": "zone_secret",
            "PARKING_COMMAND_DB_USER": "parking_command_app",
            "PARKING_COMMAND_DB_PASSWORD": "parking_command_secret",
            "PARKING_QUERY_DB_USER": "parking_query_app",
            "PARKING_QUERY_DB_PASSWORD": "parking_query_secret",
        }
