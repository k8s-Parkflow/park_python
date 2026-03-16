from __future__ import annotations

import importlib
import os
from unittest import TestCase
from unittest.mock import patch


class CommandQueryHttpRuntimeSettingsTests(TestCase):
    def test_should_configure_parking_command_http_runtime_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PARKING_COMMAND_DB_USER": "parking_command_app",
                "PARKING_COMMAND_DB_PASSWORD": "parking_command_secret",
            },
            clear=False,
        ):
            settings_module = importlib.import_module("parking_command_service.settings")
            settings_module = importlib.reload(settings_module)

        self.assertEqual(
            settings_module.ROOT_URLCONF,
            "parking_command_service.http_runtime.urls",
        )
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "parking_command_service.http_runtime.wsgi.application",
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertEqual(
            settings_module.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertEqual(settings_module.DATABASES["default"]["NAME"], "autoe_parking_command")
        self.assertEqual(settings_module.DATABASES["default"]["HOST"], "127.0.0.1")
        self.assertIn(
            "parking_command_service.apps.ParkingCommandServiceConfig",
            settings_module.INSTALLED_APPS,
        )

    def test_should_configure_parking_query_http_runtime_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PARKING_QUERY_DB_USER": "parking_query_app",
                "PARKING_QUERY_DB_PASSWORD": "parking_query_secret",
            },
            clear=False,
        ):
            settings_module = importlib.import_module("parking_query_service.settings")
            settings_module = importlib.reload(settings_module)

        self.assertEqual(
            settings_module.ROOT_URLCONF,
            "parking_query_service.http_runtime.urls",
        )
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "parking_query_service.http_runtime.wsgi.application",
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertEqual(
            settings_module.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertEqual(settings_module.DATABASES["default"]["NAME"], "autoe_parking_query")
        self.assertEqual(settings_module.DATABASES["default"]["HOST"], "127.0.0.1")
        self.assertIn(
            "parking_query_service.apps.ParkingQueryServiceConfig",
            settings_module.INSTALLED_APPS,
        )
        self.assertIn("rest_framework", settings_module.INSTALLED_APPS)
