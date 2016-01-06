"""
Django settings for portal pp. This is just a harness type
project for testing and interacting with the app.


For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/

"""
import ast
import os
import platform

from django.utils.encoding import force_bytes
import dj_database_url
import yaml
import stripe

from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR

VERSION = "0.0.0"

CONFIG_PATHS = [
    os.environ.get('TEACHERSPORTAL_CONFIG', ''),
    os.path.join(os.getcwd(), 'teachersportal.yml'),
    os.path.join(os.path.expanduser('~'), 'teachersportal.yml'),
    '/etc/teachersportal.yml',
]


def load_fallback():
    """Load optional yaml config."""
    fallback_config = {}
    config_file_path = None
    for config_path in CONFIG_PATHS:
        if os.path.isfile(config_path):
            config_file_path = config_path
            break
    if config_file_path is not None:
        with open(config_file_path) as config_file:
            fallback_config = yaml.safe_load(config_file)
    return fallback_config

FALLBACK_CONFIG = load_fallback()


def get_var(name, default):
    """Return the settings in a precedence way with default."""
    try:
        value = os.environ.get(name, FALLBACK_CONFIG.get(name, default))
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_var(
    'SECRET_KEY',
    '36boam8miiz0c22il@3&gputb=wrqr2plah=0#0a_bknw9(2^r'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_var('DEBUG', False)

ALLOWED_HOSTS = get_var('ALLOWED_HOSTS', [])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'compressor',
    'widget_tweaks',
    'rest_framework',
    # Our INSTALLED_APPS
    'portal',
] + get_core_apps()

# Oscar site id
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR + '/templates/',
            OSCAR_MAIN_TEMPLATE_DIR
        ],
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

WSGI_APPLICATION = 'teachersportal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
# Uses DATABASE_URL to configure with sqlite default:
# For URL structure:
# https://github.com/kennethreitz/dj-database-url
DEFAULT_DATABASE_CONFIG = dj_database_url.parse(
    get_var(
        'DATABASE_URL',
        'sqlite:///{0}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    )
)

if get_var('PORTAL_DB_DISABLE_SSL', False):
    DEFAULT_DATABASE_CONFIG['OPTIONS'] = {}
else:
    DEFAULT_DATABASE_CONFIG['OPTIONS'] = {'sslmode': 'require'}

DATABASES = {
    'default': DEFAULT_DATABASE_CONFIG
}

CCXCON_API = get_var('CCXCON_API', None)

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Haystack is required for Oscar
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# Serve static files with dj-static
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    # defaults
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # Necessary for oscar which uses compressor
    'compressor.finders.CompressorFinder',
)

INTERNAL_IPS = (get_var('HOST_IP', '127.0.0.1'), )

# Request files from the webpack dev server
USE_WEBPACK_DEV_SERVER = get_var('PORTAL_USE_WEBPACK_DEV_SERVER', False)
WEBPACK_SERVER_URL = get_var('PORTAL_WEBPACK_SERVER_URL', 'http://{host}:8076')

# Import oscar default settings
# pylint: disable=wrong-import-position,unused-wildcard-import,wildcard-import
from oscar.defaults import *  # noqa

# Is oscar visible at /oscar/?
PORTAL_OSCAR_VISIBLE = get_var('PORTAL_OSCAR_VISIBLE', False)

# Configure e-mail settings
EMAIL_BACKEND = get_var('PORTAL_EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = get_var('PORTAL_EMAIL_HOST', 'localhost')
EMAIL_PORT = get_var('PORTAL_EMAIL_PORT', 25)
EMAIL_HOST_USER = get_var('PORTAL_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = get_var('PORTAL_EMAIL_PASSWORD', '')
EMAIL_USE_TLS = get_var('PORTAL_EMAIL_TLS', False)
EMAIL_SUPPORT = get_var('PORTAL_SUPPORT_EMAIL', 'support@example.com')
DEFAULT_FROM_EMAIL = get_var('PORTAL_FROM_EMAIL', 'webmaster@localhost')

# e-mail configurable admins
ADMIN_EMAIL = get_var('PORTAL_ADMIN_EMAIL', '')
if ADMIN_EMAIL is not '':
    ADMINS = (('Admins', ADMIN_EMAIL),)
else:
    ADMINS = ()

# Logging configuration
LOG_LEVEL = get_var('PORTAL_LOG_LEVEL', 'DEBUG')
DJANGO_LOG_LEVEL = get_var('DJANGO_LOG_LEVEL', 'DEBUG')

# For logging to a remote syslog host
LOG_HOST = get_var('PORTAL_LOG_HOST', 'localhost')
LOG_HOST_PORT = get_var('PORTAL_LOG_HOST_PORT', 514)

HOSTNAME = platform.node().split('.')[0]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'formatters': {
        'verbose': {
            'format': (
                '[%(asctime)s] %(levelname)s %(process)d [%(name)s] '
                '%(filename)s:%(lineno)d - '
                '[{hostname}] - %(message)s'
            ).format(hostname=HOSTNAME),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'syslog': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local7',
            'formatter': 'verbose',
            'address': (LOG_HOST, LOG_HOST_PORT)
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console', 'syslog'],
            'level': LOG_LEVEL,
        },
        'portal': {
            'handlers': ['console', 'syslog'],
            'level': LOG_LEVEL,
        },
        'django': {
            'propagate': True,
            'level': DJANGO_LOG_LEVEL,
            'handlers': ['console', 'syslog'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': True,
        },
        'urllib3': {
            'level': 'INFO',
        }
    },
}

# Secret used with signatures for CCXCon webhooks endpoint
CCXCON_WEBHOOKS_SECRET = force_bytes(get_var('CCXCON_WEBHOOKS_SECRET', ''))

# Oauth settings for CCXCon
CCXCON_OAUTH_CLIENT_ID = get_var("CCXCON_OAUTH_CLIENT_ID", "")
CCXCON_OAUTH_CLIENT_SECRET = get_var("CCXCON_OAUTH_CLIENT_SECRET", "")

# Stripe keys
STRIPE_PUBLISHABLE_KEY = get_var("STRIPE_PUBLISHABLE_KEY", "")
stripe.api_key = get_var("STRIPE_SECRET_KEY", "")
