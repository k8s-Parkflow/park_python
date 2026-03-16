from __future__ import annotations

from importlib import import_module

from django.test import SimpleTestCase


class OrchestrationHttpRuntimeSettingsTests(SimpleTestCase):
    def test_should_configure_orchestration_only_urlconf_and_wsgi(self) -> None:
        settings_module = import_module("orchestration_service.settings")

        self.assertEqual(
            settings_module.ROOT_URLCONF,
            "orchestration_service.http_runtime.urls",
        )
        self.assertEqual(
            settings_module.WSGI_APPLICATION,
            "orchestration_service.http_runtime.wsgi.application",
        )
        self.assertEqual(
            settings_module.INSTALLED_APPS,
            [
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "orchestration_service.apps.OrchestrationServiceConfig",
            ],
        )
        self.assertEqual(set(settings_module.DATABASES.keys()), {"default"})
        self.assertEqual(
            settings_module.DATABASES["default"]["ENGINE"],
            "django.db.backends.mysql",
        )
        self.assertEqual(settings_module.DATABASES["default"]["NAME"], "autoe_orchestration")
        self.assertEqual(settings_module.DATABASES["default"]["HOST"], "127.0.0.1")
