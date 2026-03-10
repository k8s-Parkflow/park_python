from __future__ import annotations

import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from park_py.database_config import build_service_databases


class MsaDatabaseConfigUnitTests(TestCase):
    def test_should_build_service_database_paths__when_base_dir_is_given(self) -> None:
        """[UT-MSA-DB-01] 기본 DB 파일 경로 생성"""

        databases = build_service_databases(base_dir=Path("/tmp/autoe"))

        self.assertEqual(databases["vehicle"]["NAME"], "/tmp/autoe/vehicle.sqlite3")
        self.assertEqual(databases["parking_query"]["NAME"], "/tmp/autoe/parking_query.sqlite3")

    def test_should_apply_env_override__when_database_name_is_provided(self) -> None:
        """[UT-MSA-DB-02] 환경변수 DB 경로 override"""

        with patch.dict(os.environ, {"VEHICLE_DB_NAME": "/var/db/vehicle.sqlite3"}, clear=False):
            databases = build_service_databases(base_dir=Path("/tmp/autoe"))

        self.assertEqual(databases["vehicle"]["NAME"], "/var/db/vehicle.sqlite3")
