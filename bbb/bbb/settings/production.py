# flake8: NOQA: F403,F405
import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

from bbb.settings import *

ALLOWED_HOSTS = ["*"]

DEBUG = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = False  # for public apps, set to True
SECURE_REDIRECT_EXEMPT = [r"^healthcheck$"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Uncomment if you want to access admin pages via private proxy
# CSRF_TRUSTED_ORIGINS = ["https://<project domain>.n8s.jp"]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or SECRET_KEY


##############
# Sentry-SDK #
##############
# https://docs.sentry.io/product/performance/getting-started/?platform=python
# https://docs.sentry.io/platforms/python/guides/django/
# https://docs.sentry.io/product/sentry-basics/environments/

ignore_logger("django.security.DisallowedHost")

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.WARNING,  # Send errors as events
)
sentry_sdk.init(
    integrations=[sentry_logging],
    release=APP_VERSION,
    environment="production",
    dsn=SENTRY_DSN,
)


####################
# Your application #
####################

# DATABASES = {
#     "default": dj_database_url.config()
# }
