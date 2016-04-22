# Django settings for imam project.

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

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files to collect
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, '../webapp/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

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

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures'),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)

# A sample logging configuration.
# This logs all rapidsms messages to the file named in DJANGO_LOG_FILE_NAME
LOG_FILE_NAME = '/var/log/imamd/rapidsms.log'
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

INSTALLED_APPS = (
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
    "rapidsms.router.db",
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
    "mailqueue"
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

RAPIDSMS_ROUTER = "rapidsms.router.db.DatabaseRouter"

PAGE_SIZE = 25

DATETIME_FORMAT = '%H:%M:%S %d-%m-%Y'

LOGIN_REDIRECT_URL = '/'

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.database.DatabaseBackend",
    }
}   # more RapidSMS backends will be added by Salt

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

djcelery.setup_loader()

from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'reminders': {
        'task': 'core.tasks.reminders',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}
RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN'),
}
