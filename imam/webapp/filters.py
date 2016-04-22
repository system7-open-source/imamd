from __future__ import unicode_literals
from datetime import date

from django import forms
from django.db.models import Max, Min
import django_filters
from django.utils.translation import ugettext as _

from core.models import Personnel, Position, Program, ProgramCategory, \
    ProgramReport, StockReport, StockOutReport
from locations.models import Location
from core.utils import iso_normalize


CATEGORY_CHOICES = list(
    ProgramCategory.objects.all().values_list('pk', 'acronym'))
POSITION_CHOICES = list(Position.objects.all().values_list('pk', 'description'))
PROGRAM_CHOICES = list(Program.objects.all().values_list(
    'pk', 'code'))  # exclude(code='SFP').values_list('pk', 'code'))
try:
    MAX_DATE = ProgramReport.objects.aggregate(Max('report_date')).values()[0]
except Exception:  # todo: this exception clause is too broad
    MAX_DATE = iso_normalize(date.today())
if MAX_DATE is None:
    MAX_DATE = iso_normalize(date.today())
try:
    MIN_DATE = ProgramReport.objects.aggregate(Min('report_date')).values()[0]
except Exception:  # todo: this exception clause is too broad
    MIN_DATE = iso_normalize(date.today())
if MIN_DATE is None:
    MIN_DATE = iso_normalize(date.today())

YEAR_CHOICES = [
    (year, str(year)) for year in xrange(MAX_DATE.year, MIN_DATE.year - 1, -1)
]


def make_period_choices():
    return [('w{}'.format(week), 'week {}'.format(week)) for week in
            range(1, 54)]


class LocationChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        super(LocationChoiceFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            try:
                location = Location.objects.get(pk=value)
                descendant_sites = Location.get_sites(
                    location.get_descendants())
                return qs.filter(site__in=descendant_sites)
            except Location.DoesNotExist:
                return qs.none()

        return qs


class SiteChoiceFilter(LocationChoiceFilter):
    def filter(self, qs, value):
        if value:
            try:
                location = Location.objects.get(pk=value)
                sublocation_pks = Location.get_sites(
                    location.get_descendants()).values_list('pk', flat=True)
                return qs.filter(pk__in=sublocation_pks)
            except Location.DoesNotExist:
                return qs.none()

        return qs


class PersonnelLocationChoiceFilter(LocationChoiceFilter):
    def filter(self, qs, value):
        if value:
            try:
                location = Location.objects.get(pk=value)
                descendant_loc_pks = location.get_descendants(
                    include_self=True).values_list('pk', flat=True)
                return qs.filter(site__pk__in=descendant_loc_pks)
            except Location.DoesNotExist:
                return qs.none()

        return qs


class PositionChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [('', '')] + POSITION_CHOICES
        super(PositionChoiceFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            try:
                position = Position.objects.get(pk=value)

                return qs.filter(position=position)
            except Position.DoesNotExist:
                return qs.none()

        return qs


class CategoryChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [('', '')] + CATEGORY_CHOICES
        super(CategoryChoiceFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            try:
                category = ProgramCategory.objects.get(pk=value)

                return qs.filter(category=category)
            except ProgramCategory.DoesNotExist:
                return qs.none()

        return qs


class PeriodChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [('', '')] + make_period_choices()
        super(PeriodChoiceFilter, self).__init__(*args, **kwargs)


class ProgramChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [('0', _('All'))] + PROGRAM_CHOICES
        super(ProgramChoiceFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            return qs.filter(program__pk=value)

        return qs


class YearChoiceFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = YEAR_CHOICES
        if 'initial' not in kwargs:
            kwargs['initial'] = MAX_DATE.year
        super(YearChoiceFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            return qs.filter(created__year=value)

        return qs


class ReportedYearChoiceFilter(YearChoiceFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(report_date__year=value)
        return qs


class SiteFilterSet(django_filters.FilterSet):
    location = LocationChoiceFilter(widget=forms.HiddenInput())

    class Meta:
        model = Location


class PersonnelFilterSet(django_filters.FilterSet):
    location = PersonnelLocationChoiceFilter(
        widget=forms.HiddenInput()
    )
    position = PositionChoiceFilter(
        widget=forms.Select({'class': 'select-two'})
    )

    class Meta:
        model = Personnel


class ProgramReportFilterSet(django_filters.FilterSet):
    location = LocationChoiceFilter(widget=forms.HiddenInput())
    year = ReportedYearChoiceFilter(
        widget=forms.Select({'class': 'select-two'})
    )
    period_number = PeriodChoiceFilter(
        widget=forms.Select({'class': 'select-two'})
    )
    program = ProgramChoiceFilter(widget=forms.Select({'class': 'select-two'}))

    class Meta:
        model = ProgramReport
        fields = []


class StockOutReportFilterSet(django_filters.FilterSet):
    location = LocationChoiceFilter(
        widget=forms.Select({'class': 'select-two'}))
    year = YearChoiceFilter(widget=forms.Select({'class': 'select-two'}))

    class Meta:
        model = StockOutReport
        fields = []


class StockReportFilterSet(django_filters.FilterSet):
    location = LocationChoiceFilter(widget=forms.HiddenInput())
    start = django_filters.DateFilter(name='created', lookup_type='gte',
                                      input_formats=['%d/%m/%Y', '%d/%m/%y'])
    end = django_filters.DateFilter(name='created', lookup_type='lte',
                                    input_formats=['%d/%m/%Y', '%d/%m/%y'])

    class Meta:
        model = StockReport
        fields = []
