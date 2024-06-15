import os


def _get_app_dirnames():
    dir = os.path.dirname(__file__)
    for dir_name in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, dir_name)):
            yield dir_name


INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    *[f"samples.{app}" for app in _get_app_dirnames()],
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
    }
}
ROOT_URLCONF = None
USE_TZ = True
SECRET_KEY = "test"

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
