"""
Django settings for imgpredict project.
"""

import os
from pathlib import Path

from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security settings — now read from environment variables in production.
# Locally, if these env vars aren't set, the same values you already had
# are used as defaults, so nothing changes for your local dev workflow.
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-s01bk7-i!b=)$%9g)&#*$x68a_au(^ubdrjq5)$o#$d0xfkw_3",  # local fallback only
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    ".onrender.com",
    "127.0.0.1",
    "localhost",
    "192.168.1.68",
    "192.168.254.5",
    "192.168.61.236",
    "169.254.36.194",
    "192.168.137.253"


]


# Application definition

INSTALLED_APPS = [
    "crispy_tailwind",
    "crispy_forms",
    "prediction",
    "account",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # added: serves static files on Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "imgpredict.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "imgpredict.wsgi.application"
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static & media files
# FIXED: STATIC_ROOT was previously pointing at BASE_DIR itself (the whole
# project folder) — that risks collectstatic dumping files mixed in with
# your source code. It's now a separate "staticfiles" folder, which is the
# standard, safe convention.
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"


X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ---------------------------------------------------------------------------
# Email — credentials now read from environment variables instead of being
# hardcoded in the file (important since this file will be pushed to
# GitHub for deployment — a hardcoded password there is publicly visible).
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "sandbox.smtp.mailtrap.io")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "949cbabf7ea302")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "2aa75e3dc8f9cc")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "2525")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
