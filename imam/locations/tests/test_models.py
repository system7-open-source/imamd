__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'

from model_mommy import mommy

import django.db
import django.utils.timezone
import django.test
import django.forms.models

import locations.models


class LocationTypeTest(django.test.TestCase):
    def test_code_field_unique(self):
        """Issue 112 suggests that the code field should be unique.
        """
        mommy.make(locations.models.LocationType, code='adm0', _quantity=1)
        # no second object with the same code allowed
        with self.assertRaisesRegexp(
                django.db.IntegrityError,
                r'.*code.*already exists\..*'):
            mommy.make(locations.models.LocationType, code='adm0', _quantity=1)


