from .settings import *  # noqa: F403


def _build_test_database_name(alias: str, config: dict[str, str]) -> str:
    return f"test_{alias}_{config['NAME']}"


DATABASES = {  # type: ignore[name-defined]
    alias: {
        **config,
        "TEST": {
            "NAME": _build_test_database_name(alias, config),
        },
    }
    for alias, config in DATABASES.items()  # type: ignore[name-defined]
}

if "django.contrib.admin" in INSTALLED_APPS:  # type: ignore[name-defined]
    INSTALLED_APPS = [  # type: ignore[name-defined]
        app for app in INSTALLED_APPS if app != "django.contrib.admin"
    ]

ROOT_URLCONF = "park_py.urls_test"
