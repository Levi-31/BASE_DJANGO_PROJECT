"""
Staging environment settings.

Usage:
    python3 manage.py runserver --settings=config.staging
"""

from config.base import *  # noqa: F401,F403

# ──────────────────────────────────────────────
# Debug
# ──────────────────────────────────────────────
DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="staging.example.com", cast=Csv())

# ──────────────────────────────────────────────
# Security hardening
# ──────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)

# ──────────────────────────────────────────────
# Database — staging credentials from env
# ──────────────────────────────────────────────
DATABASES["default"].update(
    {
        "NAME": config("DB_NAME", default="hld_project_staging"),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="3306"),
    }
)

# ──────────────────────────────────────────────
# Cache — staging Redis
# ──────────────────────────────────────────────
CACHES["default"]["LOCATION"] = config(
    "REDIS_URL", default="redis://127.0.0.1:6379/1"
)

# ──────────────────────────────────────────────
# CORS — restricted in staging
# ──────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = False

# ──────────────────────────────────────────────
# DRF — JSON only, auth required
# ──────────────────────────────────────────────
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
]
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.IsAuthenticated",
]

# ──────────────────────────────────────────────
# Logging — less verbose in staging
# ──────────────────────────────────────────────
LOGGING["root"]["level"] = "WARNING"
