"""
Django settings for openchat project.

Generated by 'django-admin startproject' using Django 1.9.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import random
import string


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
print(os.path.join(BASE_DIR, 'collected-static'))


def random_str(n=50):
    chars = ''.join([string.ascii_letters, string.digits, string.punctuation]
                    ).replace('\'', '').replace('"', '').replace('\\', '')
    return ''.join([random.SystemRandom().choice(chars) for i in range(n)])


try:
    from .local_settings import SECRET_KEY, DEBUG
except ImportError:
    SECRET_KEY = random_str()
    DEBUG = True

try:
    from .local_settings import DATABASES as LOCAL_DATABASES
except ImportError:
    LOCAL_DATABASES = {'default': {}, }


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY or os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # need to store the new key somehwere that the other gunicorn instances can find it too!
    os.environ["DJANGO_SECRET_KEY"] = random_str()
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [
    'openchat',
    'totalgood.org',
    'openchat.totalgood.org',
    'openchat.totalgood.test',
    'big.openchat.totalgood.org',
    '34.211.189.63',
    'localhost',
    '127.0.0.1',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.gis',  # FIXME: Zak needs this!!!!!

    'rest_framework',
    'django_extensions',
    'django_celery_results',

    'openspaces',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'openchat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'openchat.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('DATABASE_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        # 'HOST': 'localhost',
        # 'PORT': 5432,
        # 'USER': os.getenv('DATABASE_USER', 'postgres'),
        # 'PASSWORD': os.getenv('DATABASE_PASSWORD', '')
    },
}


for k in LOCAL_DATABASES:
    DATABASES[k].update(LOCAL_DATABASES[k])


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT = None
# os.path.join(BASE_DIR, 'collected-static')

STATIC_URL = '/static/'
STATIC_ROOT = '/srv/openchat/collected-static'


REST_FRAMEWORK = {
    'PAGE_SIZE': 30,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer', ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',)
}

# APPS_TO_REST = ['openspaces']

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'django': {
#             'format': 'django: %(message)s',
#         },
#     },

#     'handlers': {
#         'logging.handlers.SysLogHandler': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.SysLogHandler',
#             'facility': 'local7',
#             'formatter': 'django',
#             'address': '/dev/log',
#         },
#     },

#     'loggers': {
#         'loggly': {
#             'handlers': ['logging.handlers.SysLogHandler'],
#             'propagate': True,
#             'format': 'django: %(message)s',
#             'level': 'DEBUG',
#         },
#     }
# }


# settings for celery tasks
# CELERY_BROKER_HOST = "127.0.0.1"
# CELERY_BROKER_HOST = "0.0.0.0"
# CELERY_BROKER_PORT = 5672  # default RabbitMQ listening port
# CELERY_BROKER_USER = "admin"
# CELERY_BROKER_PASSWORD = "mypass"
# CELERY_BROKER_VHOST = "hackor"
# CELERY_RESULT_BACKEND = 'amqp'

CELERY_IMPORTS = ('openspaces.tasks',)
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# CELERY_BROKER_URL = 'rabbit://admin:mypass@localhost:5672//'
CELERY_ALWAYS_EAGER = False
CELERY_RESULT_BACKEND = 'django-db'
