from .base import *

DEBUG = False

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic"
] + INSTALLED_APPS

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("DB_POSTGRES_DB"),
        "USER": env("DB_POSTGRES_USER"),
        "PASSWORD": env("DB_POSTGRES_PASSWORD"),
        "HOST": env("DB_POSTGRES_HOST"),
        "PORT": 5432,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# SMTP settings
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")