from __future__ import annotations

import importlib
import os
from unittest import TestCase
from unittest.mock import patch


class MsaTestDatabaseSettingsUnitTests(TestCase):
    def test_should_build_mariadb_test_database_names__for_settings_test(self) -> None:
        """[UT-MSA-DB-03] settings_test가 MariaDB 테스트 DB 이름을 구성"""

        with patch.dict(os.environ, self._all_service_credentials(), clear=False):
            settings_module = importlib.import_module("park_py.settings_test")
            settings_module = importlib.reload(settings_module)

        self.assertEqual(
            settings_module.DATABASES["default"]["TEST"]["NAME"],
            "test_default_autoe_orchestration",
        )
        self.assertEqual(
            settings_module.DATABASES["vehicle"]["TEST"]["NAME"],
            "test_vehicle_autoe_vehicle",
        )
        self.assertNotIn("/", settings_module.DATABASES["default"]["TEST"]["NAME"])

    def test_should_build_mariadb_test_database_names__for_settings_msa_test(self) -> None:
        """[UT-MSA-DB-04] settings_msa_test가 MariaDB 테스트 DB 이름을 구성"""

        with patch.dict(os.environ, self._all_service_credentials(), clear=False):
            settings_module = importlib.import_module("park_py.settings_msa_test")
            settings_module = importlib.reload(settings_module)

        self.assertEqual(
            settings_module.DATABASES["parking_command"]["TEST"]["NAME"],
            "test_parking_command_autoe_parking_command",
        )
        self.assertEqual(
            settings_module.DATABASES["parking_query"]["TEST"]["NAME"],
            "test_parking_query_autoe_parking_query",
        )
        self.assertNotIn("/", settings_module.DATABASES["parking_query"]["TEST"]["NAME"])

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
