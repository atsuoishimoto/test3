# flake8: NOQA : F403, F405
import os

from bbbb.settings.test import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["MYSQL_DATABASE"],
        "HOST": os.environ["MYSQL_HOST"],
        "PORT": 3306,  # type:ignore
        "USER": os.environ["MYSQL_USER"],
        "PASSWORD": os.environ["MYSQL_PASSWORD"],
        "CONN_MAX_AGE": 0,  # type:ignore
        "OPTIONS": {"connect_timeout": 1},  # type:ignore
    }
}
