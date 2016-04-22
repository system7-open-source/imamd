# this system uses structured settings.py as defined in http://www.slideshare.net/jacobian/the-best-and-worst-of-django
import os

os.environ.setdefault('DJANGO_LOG_FILE_NAME', '/tmp/imam.log')

try:
    from staging import *
except ImportError:
    import sys, django
    django.utils.six.reraise(RuntimeError, *sys.exc_info()[1:])  # use RuntimeError to extend the traceback
except:
    raise

WSGI_APPLICATION = None

DATABASES = {  # Note: these settings may be overridden by dotenv_settings.py
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'imam_test',
        'USER': 'imamd_db_user',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'OPTIONS': { }
    },
}


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Test User', 'test@test.com'),
)

MANAGERS = ADMINS

# see: http://docs.djangoproject.com/en/dev/ref/settings/#databases

# need to have CELERY_ALWAYS_EAGER True and BROKER_BACKEND as memory
# to run tasks immediately while testing
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'


if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    import subprocess
    subprocess.call(["rm", "-r", MEDIA_ROOT])

    #TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
    TEMPLATE_STRING_IF_INVALID = ''
else:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')
    TEMPLATE_STRING_IF_INVALID = ''
