# this system uses structured settings.py as defined in http://www.slideshare.net/jacobian/the-best-and-worst-of-django

import os
os.environ.setdefault('DJANGO_LOG_FILE_NAME', '/var/log/imamd/django.log')

try:
    from ..settings import *
except ImportError:
    import sys, django
    django.utils.six.reraise(RuntimeError, *sys.exc_info()[1:])  # use RuntimeError to extend the traceback
except:
    raise

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEMPLATE_STRING_IF_INVALID = ''

TIME_ZONE = 'Africa/Lagos'

# override to set the actual location for the production static and media directories
#MEDIA_ROOT = '/var/imam-media'
#STATIC_ROOT = "/srv/imam-static"

ADMINS = (
    ('Tomasz Kotarba', 'tomasz@system7.IT'),
)

MANAGERS = ADMINS

#from .envtemplate we have...
# DATABASE_URL=Something
try:
    BROKER_URL
except NameError:
    BROKER_URL = 'amqp://guest:guest@localhost:5672/imam'
# SENDSMS_URL=http://127.0.0.1:13013/cgi-bin/sendsms
# SENDSMS_SMSC=something
# SENDSMS_SENDER=something
# SENDSMS_USERNAME=something
# SENDSMS_PASSWORD=something
BULKSMS_URL = 'http://127.0.0.1:13013/cgi-bin/sendsms'
# BULKSMS_SMSC=something
# BULKSMS_SENDER=something
# BULKSMS_USERNAME=something
# BULKSMS_PASSWORD=something
# RAVEN_DSN=something

#postgres
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

ALLOWED_HOSTS = ['.kotarba.net', '.system7.IT' ,'.unicef.org', '']

CRISPY_TEMPLATE_PACK = 'bootstrap'

EMAIL_HOST = 'smtp.gmail.com'  #The host to use for sending email.

EMAIL_HOST_PASSWORD = os.environ.get("FORMHUB_EMAIL_PASSWORD", "12345678")
#Password to use for the SMTP server defined in EMAIL_HOST.
EMAIL_HOST_USER = 'do.not.reply@system7.IT'

EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "do.not.reply@system7.IT"

import sys
if len(sys.argv) >= 2 and (sys.argv[1] == "test" or sys.argv[1] == "test_all"):
    # This trick works only when we run tests from the command line.
    TESTING_MODE = True
else:
    TESTING_MODE = False

if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    import subprocess
    subprocess.call(["rm", "-r", MEDIA_ROOT])
    # need to have CELERY_ALWAYS_EAGER True and BROKER_BACKEND as memory
    # to run tasks immediately while testing
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'

os.environ.setdefault('EMAIL_TEST_RECIPIENT', 'tomasz@system7.IT')

SECRET_KEY = 'your-secret-key'
