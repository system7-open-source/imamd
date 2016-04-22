"""
this preset uses a url-type string to implement 12-factor configuration with fewer environment variables.

DATABASE_URL = '<engine>://<user>:<password>@<host>:<port>/<database>'? <switches>
       <engine> can be one of: 'postgresql', 'postgis', 'mysql', 'sqlite'
       (default: sqlite3 database file)
   (the appropriate database modules must be loaded, of course.)

if <switches> are defined, keywords "staging" and "secrect_key" have effect as follows

SECRET_KEY  will be set from ?secret_key=<key of your invention>

if ?staging=true
  then this module will import staging.py
  otherwise, it will import production.py
"""
import os
import sys
import dotenv

#  may also do "lazy" imports of:
# import django.utitls.six
# import _database_url # local module
# import local_preset
#
# This module is compatible with ideas from:
#   dj_database_url by Kenneth Reitz
#

DATABASES = NotImplemented   # before leaving this module, we will test to ensure that this has been defined
DATABASE_URL_QUERIES = {}

_url = os.getenv('DATABASE_URL', '')

print('DATABASE_URL="{}"'.format(_url))

if _url:
    import _database_url
    _dbd, DATABASE_URL_QUERIES = _database_url.config(_url)
    _staging = DATABASE_URL_QUERIES.get('staging', ['No'])[0].lower() == 'true'

try:  # we must trap ImportError to get a quality traceback in case of errors in our parent settings files
    if _url:
        if not _staging:
            from production import *
        else:
            from staging import *
        # database definition from URL overrides others
        try:
            DATABASES['default'].update(_dbd)
        except TypeError:
            DATABASES = {'default': _dbd}
        try:
            SECRET_KEY = DATABASE_URL_QUERIES['secret_key'][0]
        except KeyError:
            pass

    #   if _url was not defined, we will use staging as a default
    else:
        from staging import *

    #  use another file for common things
    from common_settings import *
except ImportError:
    import django.utils.six
    django.utils.six.reraise(RuntimeError, *sys.exc_info()[1:])  # use RuntimeError to extend the traceback
except:
    raise


# last of all, if nothing has defined a database, use sqlite
if DATABASES is NotImplemented:
    print('No database defined in settings {}'.format(os.path.abspath(__file__)))
