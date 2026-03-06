from .settings import *  # noqa: F403

if str(BASE_DIR / "services" / "parking-query-service" / "test") not in sys.path:  # type: ignore[name-defined]
    sys.path.insert(0, str(BASE_DIR / "services" / "parking-query-service" / "test"))  # type: ignore[name-defined]

# coverage 기반 테스트 실행 시 django admin autodiscover 충돌을 피하기 위한 설정
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django.contrib.admin"]  # type: ignore[name-defined]
ROOT_URLCONF = "park_py.urls_test"
