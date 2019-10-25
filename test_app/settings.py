DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "HOST": "",
        "NAME": ":memory:",
        "PASSWORD": "",
        "PORT": "",
        "USER": "",
    }
}

INSTALLED_APPS = ("django.contrib.contenttypes", "test_app")  # to be slightly realistic

SECRET_KEY = "hunter2"

# STFU
SILENCED_SYSTEM_CHECKS = ("1_7.W001",)
