"""Staging settings and globals."""


from os import environ
from base import *
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

# HOST CONFIGURATION
ALLOWED_HOSTS = []

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')
EMAIL_PORT = environ.get('EMAIL_PORT', 587)
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER

# DATABASE CONFIGURATION
DATABASES = {}

# CACHE CONFIGURATION
CACHES = {}

# SECRET CONFIGURATION
SECRET_KEY = get_env_setting('SECRET_KEY')
