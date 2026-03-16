from __future__ import annotations

import os

from shared.database_config import build_mariadb_database

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-v!p4)rh+va8o*21jdj#e*v&^7gg=0nm)y+74_zc(_mis8%lph6",
)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "orchestration_service.apps.OrchestrationServiceConfig",
]

MIDDLEWARE = [
    "shared.error_handling.ExceptionHandlingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    #"django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "orchestration_service.http_runtime.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "orchestration_service.http_runtime.wsgi.application"

DATABASES = {
    "default": build_mariadb_database(
        name=os.getenv("ORCHESTRATION_DB_NAME", "autoe_orchestration"),
        host=os.getenv("ORCHESTRATION_DB_HOST", "127.0.0.1"),
        port=os.getenv("ORCHESTRATION_DB_PORT", "3306"),
        user=os.getenv("ORCHESTRATION_DB_USER", "root"),
        password=os.getenv("ORCHESTRATION_DB_PASSWORD", ""),
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
