from __future__ import annotations

from importlib import import_module
from unittest import TestCase


class MsaTestDatabaseSettingsUnitTests(TestCase):
    def test_should_build_mariadb_test_database_names__for_settings_test(self) -> None:
        """[UT-MSA-DB-03] settings_test가 MariaDB 테스트 DB 이름을 구성"""

        settings_module = import_module("park_py.settings_test")

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

        settings_module = import_module("park_py.settings_msa_test")

        self.assertEqual(
            settings_module.DATABASES["parking_command"]["TEST"]["NAME"],
            "test_parking_command_autoe_parking_command",
        )
        self.assertEqual(
            settings_module.DATABASES["parking_query"]["TEST"]["NAME"],
            "test_parking_query_autoe_parking_query",
        )
        self.assertNotIn("/", settings_module.DATABASES["parking_query"]["TEST"]["NAME"])
