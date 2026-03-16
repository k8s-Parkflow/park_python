from __future__ import annotations

import importlib
import os
from unittest import TestCase
from unittest.mock import patch


class InternalServiceHttpRuntimeSettingsTests(TestCase):
    def test_should_configure_vehicle_http_runtime_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VEHICLE_DB_USER": "vehicle_app",
                "VEHICLE_DB_PASSWORD": "vehicle_secret",
            },
            clear=False,
        ):
            settings_module = importlib.import_module("vehicle_service.settings")
            settings_module = importlib.reload(settings_module)

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

    def test_should_configure_zone_http_runtime_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ZONE_DB_USER": "zone_app",
                "ZONE_DB_PASSWORD": "zone_secret",
            },
            clear=False,
        ):
            settings_module = importlib.import_module("zone_service.settings")
            settings_module = importlib.reload(settings_module)

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
