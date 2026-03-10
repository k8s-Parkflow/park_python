from pathlib import Path

from .settings import *  # noqa: F403


TEST_DB_ROOT = BASE_DIR / ".test_dbs"  # type: ignore[name-defined]
TEST_DB_ROOT.mkdir(exist_ok=True)

DATABASES = {  # type: ignore[name-defined]
    alias: {
        **config,
        "TEST": {
            "NAME": str(TEST_DB_ROOT / f"test_{Path(config['NAME']).name}"),
        },
    }
    for alias, config in DATABASES.items()  # type: ignore[name-defined]
}

if "django.contrib.admin" in INSTALLED_APPS:  # type: ignore[name-defined]
    INSTALLED_APPS = [  # type: ignore[name-defined]
        app for app in INSTALLED_APPS if app != "django.contrib.admin"
    ]

ROOT_URLCONF = "park_py.urls_test"
