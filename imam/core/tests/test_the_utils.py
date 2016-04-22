"""
Test code for utilities package
"""
from __future__ import unicode_literals

from core.utils import Totalizer, iso_week_ends, iso_normalize, iso_week_starts, has_53_weeks, iso_weeks_in

import unittest
import datetime
import os

def assertion(seen, expected):
    assert seen == expected, 'Value is "%s". expected "%s"' % (seen, expected)


class TestTotalizer(unittest.TestCase):
    def test1(self):
        t = Totalizer({'one':1, 'three':3, 'a string': 'cotton'})
        t += {'two':2, 'three':3, 'not numeric': 'x'}
        assertion(t, {'one':1, 'two':2, 'three':6, 'a string':'cotton'})
        t += {'one':10}
        assertion(t.count, 3)
        assertion(t['one'], 11)

class TestIso(unittest.TestCase):
    def test_week_ends(self):
        assertion(iso_week_ends(23, 2014), datetime.date(2014, 6, 8))
        assertion(iso_week_ends(1,  2013), datetime.date(2013, 1, 6))
        assertion(iso_week_ends(52, 2011), datetime.date(2012, 1, 1))
        assertion(iso_week_ends(53, 2015), datetime.date(2016, 1, 3))
        assertion(iso_week_ends(1,  2016), datetime.date(2016, 1, 10))

    def test_week_zero_is_last_week_of_previous_year(self):
        assertion(iso_week_ends(0,  2016), iso_week_ends(53, 2015))
        assertion(iso_week_ends(0,  2012), iso_week_ends(52, 2011))

    def test_week_ends_this_year(self):
        now = datetime.date.today()
        y, w, d = now.isocalendar()
        offset = 7 - d
        assertion(iso_week_ends(w), now + datetime.timedelta(days=offset))

    def test_week_starts(self):
        assertion(iso_week_starts(24, 2014), datetime.date(2014, 6, 9))
        assertion(iso_week_starts(1,  2016), datetime.date(2016, 1, 4))
        assertion(iso_week_starts(53, 2015), datetime.date(2015, 12, 28))
        assertion(iso_week_starts(1,  2015), datetime.date(2014, 12, 29))
        assertion(iso_week_starts(52, 2014), datetime.date(2014, 12, 22))

    def test_week_starts_this_year(self):
        now = datetime.date.today()
        y, w, d = now.isocalendar()
        offset = d - 1
        assertion(iso_week_starts(w), now - datetime.timedelta(days=offset))


    def test_has_53_weeks(self):
        assertion(has_53_weeks(2014), False)
        assertion(has_53_weeks(2015), True)

    def test_iso_normalize(self):
        assertion(iso_normalize(datetime.date(2014, 6,  7)),  datetime.date(2014, 6, 8))
        assertion(iso_normalize(datetime.date(2014, 6,  8)),  datetime.date(2014, 6, 8))  # same day
        assertion(iso_normalize(datetime.date(2012, 12, 31)), datetime.date(2013, 1, 6))  # 52 week year
        assertion(iso_normalize(datetime.date(2009, 12, 29)), datetime.date(2010, 1, 3))  # 53 week year

    def test_iso_weeks_in(self):
        assertion(iso_weeks_in(2004), 53)
        assertion(iso_weeks_in(2007), 52)

class TestMailQueue(unittest.TestCase):
    def test_mail_sending(self):

        from mailqueue.models import MailerMessage

        new_message = MailerMessage()
        new_message.subject = "Your test worked."
        new_message.to_address = os.environ['EMAIL_TEST_RECIPIENT']

        # if using Google SMTP, the actual from address will be settings.EMAIL_HOST_USER
        new_message.from_address = "do.not.reply@your-domain.org"

        new_message.content = "Your mail was successfully transmitted at {} Z".format(datetime.datetime.utcnow())

        # Note: HTML content supersedes plain content on Google messages
        new_message.html_content = "<h1>This is HTML Mail Content</h1><br>{}".format(new_message.content)

        new_message.app = "SAM Reports"
        new_message.save()
        assert True  # always passes if it does not crash
