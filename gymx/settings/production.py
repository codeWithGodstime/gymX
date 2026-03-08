from .base import *

DEBUG = env.bool("DEBUG", False)
SECRET_KEY = env("SECRET_KEY")

INSTALLED_APPS = SHARED_APPS + TENANT_APPS + [
    "whitenoise.runserver_nostatic",
    "crispy_forms",
    "crispy_bootstrap5",
]

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("DB_POSTGRES_DB"),
        "USER": env("DB_POSTGRES_USER"),
        "PASSWORD": env("DB_POSTGRES_PASSWORD"),
        "HOST": env("DB_POSTGRES_HOST"),
        "PORT": 5432
    }
}

# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# SMTP settings
# EMAIL_HOST = env("EMAIL_HOST")
# EMAIL_PORT = env.int("EMAIL_PORT", 587)
# EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
# EMAIL_HOST_USER = env("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

SESSION_COOKIE_DOMAIN = ".gymx.jo3.org"
CSRF_COOKIE_DOMAIN = ".gymx.jo3.org"
SESSION_COOKIE_PATH = "/"
CSRF_COOKIE_PATH = "/"

# static files settings for production

STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

# # https://whitenoise.readthedocs.io/en/latest/django.html
# STORAGES = {
#     "default": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

# media files settings for production
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
AUTH_USER_MODEL = "accounts.User"

DOMAIN_HOST = env("DOMAIN_HOST")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    #     "file": {
    #         "class": "logging.FileHandler",
    #         "filename": BASE_DIR / "logs/django.log",
    #         "formatter": "verbose",
    #     },
    },

    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}