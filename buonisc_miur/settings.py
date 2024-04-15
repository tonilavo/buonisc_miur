"""
Django settings for buonisc_miur project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType
import os, sys
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = '*'
RUNPORT = env('RUNPORT')
HOSTNAME = env('HOSTNAME')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_datatables',
    'reset_migrations',
    'bootstrap4',
    'bootstrap_datepicker_plus',
    'crispy_forms',
    'access_tokens',
    'localflavor',
    'captcha',
    'front',
    'back'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'buonisc_miur.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['../back/templates'],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'buonisc_miur.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
    # read os.environ['SQLITE_URL']
    'extra': env.db('SQLITE_URL', default='sqlite:////tmp/my-tmp-sqlite.db')
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'it-IT'
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_L10N = True
USE_TZ = True
DECIMAL_SEPARATOR = ','

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

#Settings for Celery (Tasks.py)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER =  'json'
CELERY_BROKER_URL = env('CELERY_BROKER_URL')

#Settings for send email
EMAIL_HOST  = env('EMAIL_HOST')
EMAIL_HOST_USER  = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD  = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT  =  env('EMAIL_PORT')
#EMAIL_USE_TLS = env('EMAIL_USE_TLS') my server doesn't use TTLS

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 100,
}

BOOTSTRAP4 = {
    "error_css_class": "bootstrap4-error",
    "required_css_class": "bootstrap4-required",
    "javascript_in_head": True,
    "include_jquery": True,
}
# Include BOOTSTRAP4_FOLDER in path
BOOTSTRAP4_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "bootstrap4"))
if BOOTSTRAP4_FOLDER not in sys.path:
    sys.path.insert(0, BOOTSTRAP4_FOLDER)

#SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']
RECAPTCHA_PROXY={'http':env('PROXY'), 'https':env('PROXY')}

RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')

USE_ABSOLUTE_PATH = env('USE_ABSOLUTE_PATH')
ABSOLUTE_URL = env('ABSOLUTE_URL')

# Baseline configuration.
AUTH_LDAP_SERVER_URI = 'ldap://ldap01.comune.grosseto.it'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
]

AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=comune,dc=grosseto,dc=it"

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "ou=groups, dc=comune,dc=grosseto,dc=it", ldap.SCOPE_SUBTREE, "(objectClass=groupOfUniqueNames)")

AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType()

AUTH_LDAP_REQUIRE_GROUP = "cn=serviziscolastici-admin, ou=groups, dc=comune,dc=grosseto,dc=it"
#distinzione degli utenti tra attivi e staff (Amministratori)
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
 "is_active": ("cn=serviziscolastici-admin, ou=groups, dc=comune,dc=grosseto,dc=it",),
 "is_staff": ("cn=serviziscolastici-admin, ou=groups, dc=comune,dc=grosseto,dc=it",),
}

AUTH_LDAP_MIRROR_GROUPS = True
# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

#lista degli attributi copiati da LDAP in auth_user
AUTH_LDAP_USER_ATTR_MAP = {
"first_name": "givenName",
"last_name": "sn",
"email": "mail"
}

LOGIN_URL = '/back/login'
LOGOUT_REDIRECT_URL = '/back/login'
LOGIN_REDIRECT_URL= '/back/servizio'

# dir per allegati
if USE_ABSOLUTE_PATH == 'True':
    MEDIA_URL = 'http://www.comune.grosseto.it/media/buonisc_miur/'
    MEDIA_URL = env('MEDIA_URL')
    MEDIA_ROOT = '/home/django/djangotoni/produzione/progetti/dirstudioweb/media/buonisc_miur/'
    MEDIA_ROOT = env('MEDIA_ROOT')

else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SESSION_ENGINE='django.contrib.sessions.backends.file'

DATA_SCADENZA = env('DATA_SCADENZA')

APK_SERVICE=env('APK_SERVICE')
