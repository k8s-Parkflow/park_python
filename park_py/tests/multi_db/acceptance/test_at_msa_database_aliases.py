from __future__ import annotations

from pathlib import Path
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
            Path(settings_module.DATABASES["default"]["NAME"]).name,
            "orchestration.sqlite3",
        )
