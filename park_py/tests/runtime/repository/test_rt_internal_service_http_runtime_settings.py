from __future__ import annotations

import importlib
import os
import sys
from unittest import TestCase
from unittest.mock import patch


class InternalServiceHttpRuntimeSettingsTests(TestCase):
    def test_should_configure_vehicle_http_runtime_settings(self) -> None:
        self._assert_with_settings_module(
            module_name="vehicle_service.settings",
            env={
                "VEHICLE_DB_USER": "vehicle_app",
                "VEHICLE_DB_PASSWORD": "vehicle_secret",
            },
            assertion=self._assert_vehicle_settings,
        )

    def test_should_configure_zone_http_runtime_settings(self) -> None:
        self._assert_with_settings_module(
            module_name="zone_service.settings",
            env={
                "ZONE_DB_USER": "zone_app",
                "ZONE_DB_PASSWORD": "zone_secret",
            },
            assertion=self._assert_zone_settings,
        )

    def _assert_with_settings_module(
        self,
        *,
        module_name: str,
        env: dict[str, str],
        assertion,
    ) -> None:
        with patch.dict(os.environ, env, clear=True):
            self._clear_module_cache(module_name)
            try:
                settings_module = importlib.import_module(module_name)
                assertion(settings_module)
            finally:
                self._clear_module_cache(module_name)

    def _assert_vehicle_settings(self, settings_module) -> None:
        self.assertEqual(settings_module.ROOT_URLCONF, "vehicle_service.http_runtime.urls")
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "vehicle_service.http_runtime.wsgi.application",
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertEqual(
            settings_module.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertEqual(settings_module.DATABASES["default"]["NAME"], "autoe_vehicle")
        self.assertEqual(settings_module.DATABASES["default"]["HOST"], "127.0.0.1")
        self.assertIn("vehicle_service.apps.VehicleServiceConfig", settings_module.INSTALLED_APPS)

    def _assert_zone_settings(self, settings_module) -> None:
        self.assertEqual(settings_module.ROOT_URLCONF, "zone_service.http_runtime.urls")
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "zone_service.http_runtime.wsgi.application",
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertEqual(
            settings_module.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertEqual(settings_module.DATABASES["default"]["NAME"], "autoe_zone")
        self.assertEqual(settings_module.DATABASES["default"]["HOST"], "127.0.0.1")
        self.assertIn("zone_service.apps.ZoneServiceConfig", settings_module.INSTALLED_APPS)

    @staticmethod
    def _clear_module_cache(module_name: str) -> None:
        sys.modules.pop(module_name, None)
