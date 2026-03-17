from __future__ import annotations

import importlib
import os
import sys
from unittest import TestCase
from unittest.mock import patch


class OrchestrationHttpRuntimeSettingsTests(TestCase):
    def test_should_configure_orchestration_only_urlconf_and_wsgi(self) -> None:
        self._assert_with_settings_module(
            module_name="orchestration_service.settings",
            env={
                "ORCHESTRATION_DB_USER": "orchestration_app",
                "ORCHESTRATION_DB_PASSWORD": "orchestration_secret",
            },
            assertion=self._assert_orchestration_settings,
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

    def _assert_orchestration_settings(self, settings_module) -> None:
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

    @staticmethod
    def _clear_module_cache(module_name: str) -> None:
        sys.modules.pop(module_name, None)
