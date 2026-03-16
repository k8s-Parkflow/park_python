from __future__ import annotations

import os
from unittest import TestCase
from unittest.mock import patch

from park_py.database_config import build_service_mariadb_databases


class MsaDatabaseConfigUnitTests(TestCase):
    def test_should_build_service_database_configs__when_defaults_are_used(self) -> None:
        """[UT-MSA-DB-01] 기본 MariaDB 연결 설정 생성"""

        databases = build_service_mariadb_databases()

        self.assertEqual(databases["vehicle"]["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(databases["vehicle"]["NAME"], "autoe_vehicle")
        self.assertEqual(databases["vehicle"]["HOST"], "127.0.0.1")
        self.assertEqual(databases["vehicle"]["PORT"], "3306")
        self.assertEqual(databases["vehicle"]["USER"], "root")
        self.assertEqual(databases["vehicle"]["PASSWORD"], "")
        self.assertEqual(databases["vehicle"]["OPTIONS"], {"charset": "utf8mb4"})
        self.assertEqual(databases["parking_query"]["NAME"], "autoe_parking_query")

    def test_should_apply_env_override__when_database_connection_is_provided(self) -> None:
        """[UT-MSA-DB-02] 환경변수 MariaDB 연결 override"""

        overrides = {
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
