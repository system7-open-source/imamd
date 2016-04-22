"""
This is the settings file meant to be used for local installations for
development.  Please tailor this to your own needs before running IMAMD.
"""
__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'


DEBUG = True
TEMPLATE_DEBUG = DEBUG


import os


# The top directory for this project. Contains requirements/, manage.py,
# and README.rst, a imam directory with settings etc (see
# PROJECT_PATH), as well as a directory for each Django app added to this
# project.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

# The directory with this project's templates, settings, urls, static dir,
# wsgi.py, fixtures, etc.
PROJECT_PATH = os.path.join(PROJECT_ROOT, 'imam')


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Africa/Lagos'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/public/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/public/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files to collect
STATICFILES_DIRS = (
    # os.path.join(PROJECT_ROOT, 'webapp/static'),
    os.path.join(PROJECT_ROOT, 'bower_components'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)

COMPRESS_ENABLED = True


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'imam.urls'

# # Python dotted path to the WSGI application used by Django's runserver.
# WSGI_APPLICATION = 'wsgi.application'
#
# TEMPLATE_DIRS = (
# os.path.join(PROJECT_PATH, 'templates'),
# )
#
# FIXTURE_DIRS = (
#     os.path.join(PROJECT_PATH, 'fixtures'),
# )
#
# LOCALE_PATHS = (
#     os.path.join(PROJECT_PATH, 'locale'),
# )

# A sample logging configuration.
# This logs all rapidsms messages to the file named in DJANGO_LOG_FILE_NAME
# LOG_FILE_NAME = '/var/log/imamd/rapidsms.log'
LOG_FILE_NAME = '/tmp/imam.log'  # for testing, added by T
# It also sends an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

os.environ.setdefault('DJANGO_LOG_FILE_NAME', LOG_FILE_NAME)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'basic': {
            'format': '%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'basic',
            'filename': os.getenv('DJANGO_LOG_FILE_NAME'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'rapidsms': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

INSTALLED_APPS = [
    'adminactions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'admin_keyboard_shortcuts',
    'django.contrib.admin',
    'django.contrib.gis',
    'raven.contrib.django.raven_compat',
    # External apps
    #"djtables",  # required by rapidsms.contrib.locations
    "django_tables2",
    "selectable",
    "django_extensions",
    "djcelery",
    "bootstrap_pagination",
    "crispy_forms",
    "mptt",
    "reversion",
    "tastypie",
    # RapidSMS
    "rapidsms",
    # "rapidsms.router.db",
    "rapidsms.router.celery",
    "rapidsms.backends.database",
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.default",  # Must be last
    "locations",
    "core",
    "messagebox",
    "webapp",
    "mailqueue",
    "compressor",
    "widget_tweaks",
    "django_filters",
    "rapidpro4rapidsms",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    INTERNAL_IPS = [
        '10.0.2.2'
    ]

SOUTH_MIGRATION_MODULES = {
    'tastypie': 'ignore',
    'djcelery': 'ignore',
    'reversion': 'ignore',
    'django_extensions': 'ignore',
    'locations': 'locations.migrations'
}

RAPIDSMS_ROUTER = "rapidsms.router.celery.CeleryRouter"

PAGE_SIZE = 25

DATETIME_FORMAT = '%H:%M:%S %d-%m-%Y'

LOGIN_REDIRECT_URL = '/'

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.database.DatabaseBackend",
    },
    "rapidpro-backend": {
        "ENGINE": "rapidpro4rapidsms.RapidProBackend",
        # The following URL and token should be set to match your RapidPro
        "rapidpro_api_gateway_url": "http://127.0.0.1:8000/api/v1",
        "rapidpro_api_token": "c76a3c7630263d217a98ef9ebce4a40c865befb1"
    }
}  # more RapidSMS backends will be added by Salt

RAPIDSMS_HANDLERS = (
    'core.handlers.base.BaseHandler',
    'core.handlers.registration.RegistrationHandler',
    'core.handlers.admissions.AdmissionValidationHandler',
    'core.handlers.ipf.IPFReportHandler',
    'core.handlers.otp.OTPReportHandler',
    'core.handlers.sfp.SFPReportHandler',
    'core.handlers.stock.StockReportHandler',
    'core.handlers.stockout.StockoutReportHandler',
    'core.handlers.help.HelpHandler',
)

# settings for Celery
BROKER_URL = os.environ.get('BROKER_URL')
import djcelery
import celery.schedules
djcelery.setup_loader()

CELERYBEAT_SCHEDULE = {
    'reminders': {
        'task': 'core.tasks.reminders',
        'schedule': celery.schedules.crontab(hour=8, minute=0, day_of_week=1),
    },
}

# need to have CELERY_ALWAYS_EAGER True and BROKER_BACKEND as memory
# to run tasks immediately while testing
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'


RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN'),
}

# try:
#     from preset.staging import *
# except ImportError:
#     import sys
#     import django.utils.six
#     # use RuntimeError to extend the traceback
#     django.utils.six.reraise(RuntimeError, *sys.exc_info()[1:])
# except:
#     raise

WSGI_APPLICATION = None

DATABASES = {  # Note: these settings may be overridden by dotenv_settings.py
               'default': {
                   'ENGINE': 'django.contrib.gis.db.backends.postgis',
                   'NAME': 'imam_test',
                   'USER': 'imamd_db_user',
                   'PASSWORD': '12345678',
                   'HOST': 'localhost',
                   'OPTIONS': {}
               },
}

ADMINS = (
    ('Test User', 'test@test.com'),
)

MANAGERS = ADMINS

# see: http://docs.djangoproject.com/en/dev/ref/settings/#databases


import sys
if len(sys.argv) >= 2 and (sys.argv[1] == "test" or sys.argv[1] == "test_all"):
    TESTING_MODE = True
else:
    TESTING_MODE = False

if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    import subprocess

    subprocess.call(["rm", "-r", MEDIA_ROOT])

    TEMPLATE_STRING_IF_INVALID = ''
    # configure the project test runner
    # configure django-coverage
    TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'
    COVERAGE_USE_CACHE = False
    COVERAGE_CODE_EXCLUDES = [
        'def get_absolute_url\(self\):',
        'from .* import .*',
        'import .*', ]
    COVERAGE_PATH_EXCLUDES = [r'.svn', r'.git']
    COVERAGE_ADDITIONAL_MODULES = []
    COVERAGE_MODULE_EXCLUDES = [
        'common.views.test', '__init__', 'django',
        'tests$', 'settings$', '^urls$', 'locale$',
        'migrations',
    ]
    COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'htmlcov')
    COVERAGE_CUSTOM_REPORTS = False
else:
    TEST_RUNNER = 'django.test.runner.DiscoverRunner'

SECRET_KEY = 'mlfs33^s1l4xf6a36$0thdirgcpj%dd*sisfo6HOktYXB9y'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
