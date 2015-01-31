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

INSTALLED_APPS = [
    'django.contrib.contenttypes',  # to be slightly realistic
    'dummy',
]

SECRET_KEY = 'hunter2'
