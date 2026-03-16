from __future__ import annotations

from unittest import TestCase

from park_py import settings as settings_module


class MsaDatabaseAliasesAcceptanceTests(TestCase):
    def test_should_define_five_service_databases__when_msa_settings_are_loaded(self) -> None:
        """[AT-MSA-DB-01] 서비스별 DB alias 구성"""

        aliases = set(settings_module.DATABASES.keys())

        self.assertEqual(
            aliases,
            {"default", "vehicle", "zone", "parking_command", "parking_query"},
        )
        self.assertEqual(
            settings_module.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertEqual(settings_module.DATABASES["default"]["NAME"], "autoe_orchestration")
        self.assertEqual(settings_module.DATABASES["default"]["HOST"], "127.0.0.1")
