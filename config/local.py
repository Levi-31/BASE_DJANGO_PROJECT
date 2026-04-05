"""
Local development settings.

Usage:
    python3 manage.py runserver --settings=config.local
"""

from config.base import *  # noqa: F401,F403

# ──────────────────────────────────────────────
# Debug
# ──────────────────────────────────────────────
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ──────────────────────────────────────────────
# Database overrides (local defaults)
# ──────────────────────────────────────────────
DATABASES["default"].update(
    {
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="3306"),
    }
)

# ──────────────────────────────────────────────
# Cache — use local Redis (fallback to LocMem if Redis isn't running)
# ──────────────────────────────────────────────
# Keep the Redis config from base.py; override below only if you want
# to use an in-memory cache during development:
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#     }
# }

# ──────────────────────────────────────────────
# Email — console backend for dev
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ──────────────────────────────────────────────
# CORS — allow all origins in dev
# ──────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# ──────────────────────────────────────────────
# DRF — enable browsable API in dev
# ──────────────────────────────────────────────
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Allow unauthenticated access in dev for easier testing
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.AllowAny",
]

# ──────────────────────────────────────────────
# Logging — more verbose in dev
# ──────────────────────────────────────────────
LOGGING["root"]["level"] = "DEBUG"
