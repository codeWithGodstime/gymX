from .base import *

DEBUG = True
SECRET_KEY = "your-local-secret-key"

ALLOWED_HOSTS = [".gymx.local", "gymx.local", "localhost"]

INSTALLED_APPS = SHARED_APPS + TENANT_APPS + [
    "crispy_forms",
    "crispy_bootstrap5",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": 5432,
    }
}

SESSION_COOKIE_DOMAIN = ".gymx.local"
CSRF_COOKIE_DOMAIN = ".gymx.local"
SESSION_COOKIE_PATH = "/"
CSRF_COOKIE_PATH = "/"

DOMAIN_HOST = "http://gymx.local:8000"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mailhog"
EMAIL_PORT =  587
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = "root@localhost"

AUTH_USER_MODEL = "accounts.User"


# development.py or your development settings
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# media files settings for development
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"