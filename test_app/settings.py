DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': '',
        'NAME': ':memory:',
        'PASSWORD': '',
        'PORT': '',
        'USER': '',
    },
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',  # to be slightly realistic
    'test_app',
)

SECRET_KEY = 'hunter2'

# STFU
SILENCED_SYSTEM_CHECKS = ('1_7.W001', )
