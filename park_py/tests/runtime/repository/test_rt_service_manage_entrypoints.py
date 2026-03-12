from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase


REPO_ROOT = Path(__file__).resolve().parents[4]


class ServiceManageEntrypointRuntimeTests(SimpleTestCase):
    def test_should_boot_service_local_settings__when_service_manage_runs(self) -> None:
        cases = [
            (
                REPO_ROOT / "services/orchestration-service/src/orchestration_service/manage.py",
                "orchestration_service.settings",
            ),
            (
                REPO_ROOT / "services/vehicle-service/src/vehicle_service/manage.py",
                "vehicle_service.settings",
            ),
            (
                REPO_ROOT / "services/zone-service/src/zone_service/manage.py",
                "zone_service.settings",
            ),
            (
                REPO_ROOT / "services/parking-command-service/src/parking_command_service/manage.py",
                "parking_command_service.settings",
            ),
            (
                REPO_ROOT / "services/parking-query-service/src/parking_query_service/manage.py",
                "parking_query_service.settings",
            ),
        ]

        for manage_path, settings_module in cases:
            with self.subTest(manage_path=manage_path):
                with patch.dict(os.environ, {}, clear=True):
                    with patch.object(sys, "argv", [str(manage_path), "check"]):
                        with patch("django.core.management.execute_from_command_line") as execute:
                            runpy.run_path(str(manage_path), run_name="__main__")

                            self.assertEqual(os.environ["DJANGO_SETTINGS_MODULE"], settings_module)

                execute.assert_called_once_with([str(manage_path), "check"])
