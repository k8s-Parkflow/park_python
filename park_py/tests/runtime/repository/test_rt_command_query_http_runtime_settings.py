from __future__ import annotations

import importlib
import os
import sys
from unittest import TestCase
from unittest.mock import patch


class CommandQueryHttpRuntimeSettingsTests(TestCase):
    def test_should_configure_parking_command_http_runtime_settings(self) -> None:
        self._assert_with_settings_module(
            module_name="parking_command_service.settings",
            env={
                "PARKING_COMMAND_DB_USER": "parking_command_app",
                "PARKING_COMMAND_DB_PASSWORD": "parking_command_secret",
            },
            assertion=self._assert_parking_command_settings,
        )

    def test_should_configure_parking_query_http_runtime_settings(self) -> None:
        self._assert_with_settings_module(
            module_name="parking_query_service.settings",
            env={
                "PARKING_QUERY_DB_USER": "parking_query_app",
                "PARKING_QUERY_DB_PASSWORD": "parking_query_secret",
            },
            assertion=self._assert_parking_query_settings,
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

    def _assert_parking_command_settings(self, settings_module) -> None:
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

    def _assert_parking_query_settings(self, settings_module) -> None:
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

    @staticmethod
    def _clear_module_cache(module_name: str) -> None:
        sys.modules.pop(module_name, None)
