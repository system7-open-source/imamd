import numbers
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, SU, MO

def iso_week_ends(week, year=None):
    "the date of the last day (Sunday) of the given ISO week in the given year (default=present or past year)"
    if year is None:
        year, w, d = date.today().isocalendar()
        if week > w + 1:
            year -= 1
    return date(year, 1, 1) + relativedelta(day=4, weekday=SU, weeks=week - 1)

def iso_week_starts(week, year=None):
    'the date of the first day (Monday) of the given ISO week in the given year'
    return iso_week_ends(week, year) - timedelta(days=6)

def iso_normalize(in_date):
    "the date of the last day (Sunday) of the ISO week containing this date"
    y, w, d = in_date.isocalendar()
    return iso_week_ends(w, y)

def has_53_weeks(year):
    "year uses 53 iso weeks"
    return date(year, 12, 31).isocalendar()[0] == year

def iso_weeks_in(year):
    "returns number of ISO weeks in the given"
    return date(year, 12, 28).isocalendar()[1]


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class Totalizer(dict):

    def __init__(self, iterable=[]):
        super(Totalizer, self).__init__(iterable)
        self.count = 1 if iterable else 0

    def __iadd__(self, other):
        self.count += 1
        for key, value in other.iteritems():
            if isinstance(value, numbers.Number):
                try:
                    self[key] += value
                except KeyError:
                    self[key] = value
        return self

    def __repr__(self):
        return 'Totalizer n={} {!r}'.format(self.count, dict(self))
