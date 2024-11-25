import os

DEBUG = True

SECRET_KEY = "testing"
ROOT_URLCONF = "tests.app.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}


def _get_sample_app_dirnames():
    dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "../docs/samples"))
    for dir_name in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, dir_name)):
            yield dir_name


INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "tests",
    "django_oasis",
    *[f"samples.{app}" for app in _get_sample_app_dirnames()],
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
    },
]

USE_TZ = True


MIDDLEWARE = [
    "django_oasis.middleware.ErrorHandlerMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
