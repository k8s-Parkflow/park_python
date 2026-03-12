from __future__ import annotations

from importlib import import_module

from django.test import SimpleTestCase


class CommandQueryHttpRuntimeSettingsTests(SimpleTestCase):
    def test_should_configure_parking_command_http_runtime_settings(self) -> None:
        settings_module = import_module("parking_command_service.settings")

        self.assertEqual(
            settings_module.ROOT_URLCONF,
            "parking_command_service.http_runtime.urls",
        )
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "parking_command_service.http_runtime.wsgi.application",
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertIn(
            "parking_command_service.apps.ParkingCommandServiceConfig",
            settings_module.INSTALLED_APPS,
        )

    def test_should_configure_parking_query_http_runtime_settings(self) -> None:
        settings_module = import_module("parking_query_service.settings")

        self.assertEqual(
            settings_module.ROOT_URLCONF,
            "parking_query_service.http_runtime.urls",
        )
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "parking_query_service.http_runtime.wsgi.application",
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertIn(
            "parking_query_service.apps.ParkingQueryServiceConfig",
            settings_module.INSTALLED_APPS,
        )
        self.assertIn("rest_framework", settings_module.INSTALLED_APPS)
