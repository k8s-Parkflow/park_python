from __future__ import annotations

import importlib
import os
from unittest import TestCase
from unittest.mock import patch


class OrchestrationHttpRuntimeSettingsTests(TestCase):
    def test_should_configure_orchestration_only_urlconf_and_wsgi(self) -> None:
        with patch.dict(
            os.environ,
            {
                "ORCHESTRATION_DB_USER": "orchestration_app",
                "ORCHESTRATION_DB_PASSWORD": "orchestration_secret",
            },
            clear=False,
        ):
            settings_module = importlib.import_module("orchestration_service.settings")
            settings_module = importlib.reload(settings_module)

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
