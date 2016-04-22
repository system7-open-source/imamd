=====
IMAMD
=====

`IMAMD`_ (IMAM Dashboard) is a project developed for `UNICEF`_ and intended to leverage information technology, libre software ideals and the existing cellular network infrastructure to help in implementation and coordination of Integrated Management of Acute Malnutrition programmes on a local and national level.


Acronyms and Problem Domain Vocabulary
**************************************

IMAM
    Integrated Management of Acute Malnutrition

SAM
    Severe Acute Malnutrition


Quick Installation for Developers
*********************************

The following has been tested on Ubuntu Server 14.04 LTS (which is our target platform).  Other versions of GNU/Linux or Mac OS X will require some minor adjustments.  Please note, it is recommended to develop IMAMD using a dedicated virtual machine with our target operating system installed (even if you do use the same platform!).

#. First install all the needed dependencies::

    sudo apt-get install git postgresql-9.3 postgresql-9.3-postgis-2.1 python-virtualenv python-dev
    libpq-dev postgresql-server-dev-all

#. Then get the sources (you may want to use your username and password here)::

    git clone https://github.com/system7-open-source/imamd.git imamd

#. Now create a python virtual environment::

    virtualenv --no-site-packages imamd-venv

#. Activate the virtual environment (has to be done every time you want to run the application)::

    source imamd-venv/bin/activate

#. Enter the source code::

    cd imamd

#. Either install python requirements for a production environment::

    pip install -r requirements/production.txt

   or for development::

    pip install -r requirements/development.txt

#. Create an isolated node.js environment integrated with the newly initialised Python virtual environment::
    
    nodeenv -p  # This may take a while
    
#. Install bower in the newly created node.js environment::

    npm install -g bower

#. Create the database imam_test (ignore the errors) and enable Postgis (you may want to change password for the PostgreSQL user used by IMAMD and modify IMAMD configuration accordingly)::

    sudo -u postgres psql -f make_imam_test.sql
    sudo -u postgres psql -d imam_test -f enable_postgis.sql

#. Enter the application::

    cd imam

#. Add structure to the database::

    ./manage-test.py migrate

#. [optional] Set ``DEBUG`` to ``True`` in ``imam/imam/devel_settings.py`` (e.g. to activate django-debug-toolbar)

#. [optional] Download and load your data into the database (this may take a while)::

    git clone url-to-your-data-repository imamd-data
    ./manage-test.py loaddata imamd-data/your-data-file-name.json.gz

#. Install required bower packages::

    bower install

#. Prepare static resources (JS & CSS)::

    ./manage-test.py collectstatic

#. Run the system::

    ./manage-test.py runserver

#. See it running in a web browser by entering the url::

    http://localhost:8000/

For further options see the documentation at http://djangoproject.com.  **Please note** that whenever the command ``./manage.py`` is mentioned in the django documention, you should use ``./manage-test.py`` instead.


Operation
*********

If the ``DJANGO_SETTINGS_MODULE`` environment variable is left undefined, the environment will default to ``imam.preset.url_settings`` which has a complex method of defining the database.

#. If no environment variables are defined, it will use the database hard-coded in preset/staging.py, with staging settings (``DEBUG=True`` etc.)

#. If environment variable ``DATABASE_URL`` is defined, it is used to define the database connection. For example::

    postgis://imamd_db_user:12345678@localhost/imam_test?staging=true

   is the same as::

    DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'imam_dev',
        'USER': 'imamd_db_user',
        'PASSWORD': '12345678',
        'HOST': 'localhost',
        'OPTIONS': { } },}
    DATABASE_URL_QUERIES['staging'] = 'true'
    
#. If ``DATABASE_URL_QUERIES['staging'] == 'true'``, then ``'preset/staging.py'`` will be imported,
   otherwise ``'preset/production.py'`` will be imported.


Rebuilding Locations Data
*************************

The "Locations" data table is a complex MPTT tree structure, in which the internal indexes can become corrupted.

To refresh the indexing data in those tables, execute the following command::

    ./manage-test.py rebuild_locations_tree


Outgoing E-mail Configuration
*****************************

This project sends e-mail using the django-mail-queue application.

see http://django-mail-queue.readthedocs.org/en/latest/usage.html or the sample in ``imam/core/tests/test_the_utils.py``.

Select your SMTP mail transfer agent using the usual Django settings variables (see https://docs.djangoproject.com/en/dev/ref/settings/).

In a simple deployment, this may be best done in a preset, such as::

    # this sample sends e-mail using a Google account

    EMAIL_HOST = 'smtp.gmail.com'  #The host to use for sending email.

    # Password to use for the SMTP server defined in EMAIL_HOST.
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "12345678")

    EMAIL_HOST_USER = 'do.not.reply@yourdomain.org'

    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = "do.not.reply@yourdomain.org"

E-mail tests are sent to the address defined in environment variable EMAIL_TEST_RECIPIENT.


----

.. _IMAMD: https://github.com/system7-open-source/imamd
.. _UNICEF: http://www.unicef.org/
