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

DEBUG = False  # this setting file will not work on "runserver" -- it needs a server for static files

# override to set the actual location for the production static and media directories
#     os.path.join(PROJECT_ROOT, "static"),
#
ADMINS = (
    ('Example Admin', 'admin@your-domain.org'),
)

MANAGERS = ADMINS

# DATABASES will be set by dotenv_settings.py

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Africa/Lagos'

# IMPORTANT: ! ! !  Keep the secret key as the _last_ line in the file so SaltStack can alter it without trouble...
SECRET_KEY = 'owo^0_8i*j%0^b_z-your-secret-key-p^n)qzjh=d%&^i$dz(3kd4y!h'
