# by Richi Rod AKA @richionline / falken20
# TODO: Change the print statement for Logging
# TODO: Tag all the files with the copyright

import os
from dotenv import load_dotenv  # Manage environment vars in .env file
import dj_database_url  # For returning a Django database connection dictionary
import django_heroku
import logging

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Looking for .env file for environment vars
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

# A secret key for a particular Django installation, django-admin startproject automatically
# adds a randomly-generated SECRET_KEY to each new project
SECRET_KEY = os.getenv('SECRET_KEY', default='xsd--ammmss!!"kd(sss')

# Heroku is a server web for running the app
ENV_PRO = ('ENV_PRO' in os.environ and os.environ['ENV_PRO'].upper() == 'Y')

print(f'ENV_PRO: {ENV_PRO}')

if 'DEBUG' in os.environ:
    DEBUG = os.getenv('DEBUG')
else:
    DEBUG = not ENV_PRO

print(f'DEBUG: {DEBUG}')

# SECURITY WARNING: don't run with debug turned on in production!
if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [os.getenv('ALLOWED_HOSTS', '')]

print(f'ALLOWED_HOSTS: {ALLOWED_HOSTS}')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # My Apps
    'app_covid19data',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Simplified static file serving. Using with Heroku
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'covid19web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ROD
        'APP_DIRS': False,  # TODO: Not templates folder in every app folder?
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'covid19web.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'covid19web_DB',
        'USER': 'postgres',
        'PASSWORD': '(Postgresql-21)',
        'HOST': 'localhost',
        'PORT': '',
    },
    'secondary': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

# In production environment (in this case Heroku) it is necessary to change the DB url
if ENV_PRO:
    DATABASES['default'] = dj_database_url.config(default=os.getenv('DATABASE_URL'))

# If the application is in a dev environment without PostgreSQL or another client,
# then set SQLITE conf
if os.getenv('SQLITE', default='N').upper() == 'Y':
    print(f'DB INFO: No default DB client, set the secondary DB config (SQLITE)')
    DATABASES['default'] = DATABASES['secondary']

print(f'DATABASES: {DATABASES["default"]}')

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# The static url is the url path where a client or browser can access static files
STATIC_URL = '/static/'

# ROD: About django.contrib.staticfiles installed apps
# This generates the directory where files static files are placed when you run python manage.py collectstatic
# It is no neccessary for development environment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# This determines the locations where static files are being pulled from
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Activate Django-Heroku.
django_heroku.settings(locals())

# About Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {filename} {funcName} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console1': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console2': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        # '' is root logger
        '': {
            'handlers': ['console1'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper(),
        },
        'django': {
            'handlers': ['console2'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper(),
        },
    },
}

logging.config.dictConfig(LOGGING)

print(f'LOG LEVEL: {os.getenv("LOG_LEVEL", "INFO")}')


