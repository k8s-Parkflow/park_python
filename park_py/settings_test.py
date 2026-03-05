from .settings import *  # noqa: F403

# coverage 기반 테스트 실행 시 django admin autodiscover 충돌을 피하기 위한 설정
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.admin"]  # type: ignore[name-defined]
ROOT_URLCONF = "park_py.urls_test"
