from __future__ import unicode_literals
from datetime import date, timedelta, datetime, time
import dateutil.parser

from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, UpdateView, View, \
    TemplateView
from rapidsms.contrib.messagelog.models import Message
import reversion
from django.conf import settings

from locations.models import Location, LocationType
from core.models import PatientGroup, Personnel, Program, ProgramReport, \
    StockOutReport, StockReport
from webapp.models import PdfForms
from .filters import PersonnelFilterSet, ProgramReportFilterSet, \
    SiteFilterSet, StockOutReportFilterSet, StockReportFilterSet
from .forms import ProgramReportForm
from .form_helpers import make_personnel_filter_form_helper, \
    make_program_report_filter_form_helper, \
    make_site_filter_form_helper, make_stock_filter_form_helper
from form_helpers import make_base_program_report_filter_form_helper
from core.utils import iso_normalize, iso_week_ends, Totalizer
from filters import MAX_DATE


def get_recent_report_data():
    # initial_report_date = None
    qs = ProgramReport.objects.order_by(
        '-report_date').all()  # exclude(program__code='SFP')

    try:
        most_recent_report = qs[0]
        initial_report_date = most_recent_report.report_date
    except IndexError:
        initial_report_date = iso_normalize(date.today())

    return initial_report_date.year


def signin(request):
    request.session.clear()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            login(request, form.get_user())

            next_url = request.REQUEST.get(REDIRECT_FIELD_NAME, '')

            if not is_safe_url(url=next_url, host=request.get_host()):
                next_url = settings.LOGIN_REDIRECT_URL

            return HttpResponseRedirect(next_url)
    else:
        form = AuthenticationForm(request)

    context = RequestContext(request, {'form': form, 'page_title': 'Login'})

    return render_to_response('webapp/login.html', context)


def generate_dashboard_summary(qs, start_date,
                               end_date):  # qs is a django query set

    def epoch(dat):
        """Convert datetime.date to unix epoch microseconds for JSON transmit
        to highcharts
        """
        diff = datetime.combine(dat, time()) - datetime(1970, 1, 1)
        return int(diff.total_seconds()) * 1000

    totals = {}  # collect total information for each report date
    for report in qs:
        smry = DashboardChartSummaryItem(report).summary
        try:
            totals[report.report_date] += smry
        except KeyError:
            totals[report.report_date] = Totalizer(smry)

    if not totals:  # an empty selection produces an empty chart
        return None

    atot = []
    death_rate = []
    defaulter_rate = []
    referral_rate = []
    transfer_rate = []

    key = start_date
    while key <= end_date:
        # Add more statistics to the totalised summaries (Note: in place)
        label = epoch(key)
        try:
            summary = totals[key]
            Dtot = float(
                summary['Dcur'] + summary['Dead'] + summary['DefT'] + summary[
                    'Dmed'])
            Cout = Dtot + summary['Tout']

            atot.append((label, summary['Atot']))

            try:
                death_rate.append(
                    (label, round(summary['Dead'] / Dtot * 100, 1)))
            except:  # todo: too broad exception clause, fix
                pass
            try:
                defaulter_rate.append(
                    (label, round(summary['DefT'] / Dtot * 100, 1)))
            except:  # todo: too broad exception clause, fix
                pass
            try:
                referral_rate.append(
                    (label, round(summary['Dmed'] / Dtot * 100, 1)))
            except:  # todo: too broad exception clause, fix
                pass
            try:
                transfer_rate.append(
                    (label, round(summary['Tout'] / Cout * 100, 1)))
            except:  # todo: too broad exception clause, fix
                pass
        except KeyError:
            pass
        key += timedelta(weeks=1)

    data = {
        'start_date': [[epoch(start_date)]],
        'Atot': atot,
        'death_rate': death_rate,
        'defaulter_rate': defaulter_rate,
        'referral_rate': referral_rate,
        'transfer_rate': transfer_rate
    }

    return data


def str_to_int(string):
    try:
        value = int(string)
    except ValueError:
        value = 0
    except TypeError:
        value = 0
    return value


def dashboard(request):
    initial_data = request.session.get('filter_data', None)
    response = {'page_title': _('SAM Reports Dashboard')}

    if request.method == 'POST' or initial_data:

        if request.method == 'POST':
            year = str_to_int(request.POST.get('year', MAX_DATE.year))
            location_id = str_to_int(request.POST.get('location', 0))
            program_id = str_to_int(request.POST.get('program', 0))
        else:
            year = str_to_int(initial_data.get('year', MAX_DATE.year))
            location_id = str_to_int(initial_data.get('location', 0))
            program_id = str_to_int(initial_data.get('program', 0))

        if program_id == 0:
            programs = Program.objects.all()  # exclude(code='SFP')
        else:
            programs = Program.objects.filter(pk=program_id)
        if location_id == 0:
            location = Location.root()
            location_id = getattr(location, 'id', None)
        else:
            location = Location.objects.get(pk=location_id)
        if program_id == 0 and location == Location.root() and \
           year == date.today().year:
            response['latest_global_data'] = True
    else:
        year = MAX_DATE.year
        programs = Program.objects.all()  # exclude(code='SFP')
        program_id = ''
        location = Location.root()
        location_id = getattr(location, 'id', None)
        response['latest_global_data'] = True

    if year < 2:
        year = 2

    filter_data = {
        'year': year,
        'location': location_id,
        'program': program_id
    }
    request.session['filter_data'] = filter_data
    response['programs'] = []
    for program in programs:
        program_data = {'code': program.code,
                        'description': program.description,
                        'active_site_count': location.active_site_count(program,
                                                                        year),
                        'inactive_site_count': location.inactive_site_count(
                            program, year),
                        'reporting_site_count': location.reporting_site_count(
                            program, year)}
        response['programs'].append(program_data)

    filter_set = ProgramReportFilterSet(filter_data)
    filter_set.form.helper = make_base_program_report_filter_form_helper()
    response['filter_form'] = filter_set.form

    return render_to_response(
        'webapp/index.html', response, context_instance=RequestContext(request)
    )


class DashboardChartSummaryItem(object):
    def __init__(self, programreport):
        # period = programreport.period_number

        self.period_name = '{:%Y-%m-%d}'.format(programreport.report_date)

        self.summary = {
            'period_name': self.period_name,
            # 'group_period_name': u'{} {}'.format(
            # period_name, programreport.created.year),
            'Atot': (programreport.new_marasmic_patients or 0) +
                    (programreport.new_oedema_patients or 0) +
                    (programreport.new_relapsed_patients or 0),
            'Arel': programreport.readmitted_patients or 0,
            'Tin': programreport.patients_transferred_in or 0,
            'Tout': programreport.patients_transferred_out or 0,
            'Dead': programreport.patient_deaths or 0,
            'DefT': (programreport.confirmed_patient_defaults or 0) + (
                programreport.unconfirmed_patient_defaults or 0),
            'Dcur': programreport.patients_cured or 0,
            'Dmed': programreport.unresponsive_patients or 0,
            'End': programreport.patients_at_period_end or 0,
        }

        if programreport.pk:
            self.summary['group_period_name'] = 'w{} {}'.format(
                programreport.period_number,
                programreport.report_date.year)


class DashboardChartDataView(View):
    """View class for dashboard chart data.
    """
    filter_class = ProgramReportFilterSet
    storage_key = 'filter_data'

    def get(self, request, *args, **kwargs):

        def check_initial(data_store, key):
            if data_store is None or type(data_store) == dict and not any(
                    data_store):
                if key == 'year':
                    return iso_normalize(date.today()).year
                return None
            try:
                if data_store[key] == '':
                    if key == 'year':
                        return iso_normalize(date.today()).year
                    return None
                return data_store[key]
            except KeyError:
                if key == 'year':
                    return iso_normalize(date.today()).year
                return None

        initial_data = request.session.get(self.storage_key, None)

        year = int(check_initial(initial_data, 'year'))

        if year < 2:
            year = 2
        end_date = iso_week_ends(52, year)
        start_date = iso_week_ends(52, year - 1)

        program_id = check_initial(initial_data, 'program')

        location_id = check_initial(initial_data, 'location')
        if location_id is None:
            location_id = 1
        location = Location.objects.filter(pk=location_id).first()
        # If location not found, return an empty data set, otherwise find all
        # descendant sites of the location and proceed.
        if not isinstance(location, Location):
            return JsonResponse({})
        else:
            sites = location.get_site_descendants()

        result = ProgramReport.objects.filter(site__in=sites).filter(
            report_date__gte=start_date).filter(report_date__lte=end_date)

        if program_id is not None and program_id is not 0:
            result = result.filter(program_id=program_id)

        ds = generate_dashboard_summary(result, start_date, end_date)
        return JsonResponse(ds)


class FilteredListView(ListView):
    # todo: this class has attributes defined outside its constructor, check
    filter_class = None
    filter_form_helper = None
    storage_key = None

    def get_context_data(self, **kwargs):
        if self.filter_form_helper:
            self.filter_set.form.helper = self.filter_form_helper

        context = super(FilteredListView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title

        return context

    def get_queryset(self):
        return self.filter_set.qs

    def get(self, request, *args, **kwargs):
        initial = request.session.get(self.storage_key)
        self.filter_set = self.filter_class(
            initial, queryset=self.model._default_manager.all()
        )

        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.filter_set = self.filter_class(
            request.POST, queryset=self.model._default_manager.all()
        )
        request.session[self.storage_key] = self.filter_set.form.data
        self.object_list = self.get_queryset()
        context = self.get_context_data(object_list=self.object_list)

        return self.render_to_response(context)


class MessageListView(ListView):
    # todo: this class has attributes defined outside its constructor, check
    context_object_name = 'messages'
    page_title = _('Messages')
    paginate_by = settings.PAGE_SIZE
    queryset = Message.objects.order_by('-pk')
    template_name = 'webapp/message_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MessageListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class PersonnelListView(FilteredListView):
    context_object_name = 'workers'
    filter_class = PersonnelFilterSet
    filter_form_helper = make_personnel_filter_form_helper()
    model = Personnel
    page_title = _('Personnel')
    paginate_by = settings.PAGE_SIZE
    storage_key = 'personnel_filter'
    template_name = 'webapp/personnel_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PersonnelListView, self).dispatch(request, *args, **kwargs)


class ProgramReportListView(FilteredListView):
    context_object_name = 'reports'
    filter_class = ProgramReportFilterSet
    filter_form_helper = make_program_report_filter_form_helper()
    model = ProgramReport
    page_title = _('Program reports')
    paginate_by = settings.PAGE_SIZE
    storage_key = 'program_filter'
    template_name = 'webapp/report_list.html'

    def get_queryset(self):
        # The JS code may send the variables as empty strings or nulls which
        # Django then tries to convert to int and fails.
        try:
            report_year = int(self.request.POST.get('year', 0))
        except ValueError as e:
            if 'invalid literal for int()' in e.message:
                report_year = 0
            else:
                raise e
        try:
            program_pk = int(self.request.POST.get('program', 0))
        except ValueError as e:
            if 'invalid literal for int()' in e.message:
                program_pk = 0
            else:
                raise e
        try:
            location_pk = int(self.request.POST.get('location', 0))
        except ValueError as e:
            if 'invalid literal for int()' in e.message:
                location_pk = 0
            else:
                raise e
        query = {}
        if report_year > 0:
            query['report_date__year'] = report_year
        if program_pk > 0:
            query['program__pk'] = program_pk
        qs = self.model.objects.filter(**query)
        if location_pk > 0:
            location = Location.objects.filter(pk=location_pk).first()
            sites = location.get_site_descendants()
            qs = qs.filter(site__in=sites)
            return qs
        else:
            # If there is no location with the requested ID (or no location was
            # given to filter the query results then just return the query
            # not filtered by location (i.e. the list of reports for all
            # locations).
            return qs


class SiteListView(FilteredListView):
    # todo: this class has attributes defined outside its constructor, check
    context_object_name = 'sites'
    filter_class = SiteFilterSet
    filter_form_helper = make_site_filter_form_helper()
    model = Location
    page_title = _('Sites')
    paginate_by = settings.PAGE_SIZE
    storage_key = 'site_filter'
    template_name = 'webapp/site_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.root_pk = kwargs.get('pk')
        return super(SiteListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SiteListView, self).get_context_data(**kwargs)
        context['location_types'] = LocationType.objects.all()
        return context

    def get_queryset(self):
        location = None
        try:
            location_pk = int(self.request.POST.get('location', 0))
        except ValueError as e:
            if 'invalid literal for int()' in e.message:
                location_pk = 0
            else:
                raise e
        if location_pk > 0:
            location = Location.objects.filter(pk=location_pk).first()
        if isinstance(location, Location):
            return location.get_site_descendants()
        else:
            # If there is no location with the requested PK (or no location was
            # given to filter the query results then just return the query
            # not filtered by location (i.e. the list of all sites).
            return Location.get_sites()


class StockOutReportListView(FilteredListView):
    context_object_name = 'stockouts'
    filter_class = StockOutReportFilterSet
    model = StockOutReport
    page_title = _('Stock out alerts')
    paginate_by = settings.PAGE_SIZE
    storage_key = 'stockout_filter'
    template_name = 'webapp/stockout_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StockOutReportListView, self).dispatch(request, *args,
                                                            **kwargs)


class StockReportListView(FilteredListView):
    context_object_name = 'reports'
    filter_class = StockReportFilterSet
    filter_form_helper = make_stock_filter_form_helper()
    model = StockReport
    page_title = _('Stock reports')
    paginate_by = settings.PAGE_SIZE
    storage_key = 'stock_filter'
    template_name = 'webapp/stock_list.html'

    def get_queryset(self):
        # The JS code may send the variables as empty strings or nulls.  In case
        # of invalid dates set the offender to None and ignore (i.e. do not
        # filter by it).
        start_string = self.request.POST.get('start', '').strip()
        start = None
        if len(start_string) > 0:
            try:
                start = dateutil.parser.parse(start_string, dayfirst=True)
            except ValueError as e:
                if 'Unknown string format' not in e.message:
                    raise e

        end_string = self.request.POST.get('end', '').strip()
        end = None
        if len(end_string) > 0:
            try:
                end = dateutil.parser.parse(
                    end_string,
                    default=datetime(1, 1, 1, 23, 59, 59),
                    dayfirst=True
                )
            except ValueError as e:
                if 'Unknown string format' not in e.message:
                    raise e
        try:
            location_pk = int(self.request.POST.get('location', 0))
        except ValueError as e:
            if 'invalid literal for int()' in e.message:
                location_pk = 0
            else:
                raise e
        query = {}
        if start is not None:
            query['created__gte'] = start
        if end is not None:
            query['created__lte'] = end
        qs = self.model.objects.filter(**query)
        if location_pk > 0:
            location = Location.objects.filter(pk=location_pk).first()
            sites = location.get_site_descendants()
            qs = qs.filter(site__in=sites)
            return qs
        else:
            # If there is no location with the requested ID (or no location was
            # given to filter the query results then just return the query
            # not filtered by location (i.e. the list of reports for all
            # locations).
            return qs


class ProgramReportEditView(UpdateView):
    # todo: this class has attributes defined outside its constructor, check
    form_class = ProgramReportForm
    model = ProgramReport
    page_title = _('Edit report')
    template_name = 'webapp/report_edit.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProgramReportEditView, self).dispatch(
            request, *args, **kwargs
        )

    def form_valid(self, form):
        with reversion.create_revision():
            self.object = form.save()
            reversion.set_comment(form.cleaned_data.get('comment'))

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ProgramReportEditView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['period'] = self.object.summary()['period_name']
        context['program'] = self.object.program.code
        context['reporter'] = self.object.reporter
        context['versions'] = reversion.get_unique_for_object(self.object)
        return context

    def get_success_url(self):
        return reverse_lazy('reports')


class ProgramReportHistoryDetailView(DetailView):
    # todo: this class has attributes defined outside its constructor, check
    context_object_name = 'detail'
    page_title = _('History detail')
    template_name = 'webapp/report_history.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProgramReportHistoryDetailView, self).dispatch(request,
                                                                    *args,
                                                                    **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProgramReportHistoryDetailView, self).get_context_data(
            **kwargs)
        context['page_title'] = self.page_title

        return context

    def get_object(self, queryset=None):
        obj_id = self.kwargs.get('obj_id')
        version_id = self.kwargs.get('version_id')
        report = get_object_or_404(ProgramReport, pk=obj_id)

        versions = reversion.get_for_object(report)
        version = versions.get(pk=version_id)
        versions_pks = list(
            versions.order_by('pk').values_list('pk', flat=True))

        index = versions_pks.index(version.pk)
        num_versions = len(versions_pks)
        prev_pk = None
        next_pk = None

        if index > 0:
            prev_pk = versions_pks[index - 1]
        if index < num_versions - 1:
            next_pk = versions_pks[index + 1]

        group = PatientGroup.objects.get(pk=version.field_dict.get('group'))
        program = Program.objects.get(pk=version.field_dict.get('program'))
        reporter = Personnel.objects.get(pk=version.field_dict.get('reporter'))
        site = Location.objects.get(pk=version.field_dict.get('site'))

        return {
            'object': version,
            'prev': prev_pk,
            'next': next_pk,
            'index': index,
            'num_versions': num_versions,
            'group': group,
            'program': program,
            'reporter': reporter,
            'site': site,
            'period': report.summary()['period_name'],
        }


class ProgramReportRevertView(View):
    # todo: this class has attributes defined outside its constructor, check
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProgramReportRevertView, self).dispatch(request, *args,
                                                             **kwargs)

    def get(self):
        report_pk = self.kwargs.get('obj_id')
        version_pk = self.kwargs.get('version_id')

        report = get_object_or_404(ProgramReport, pk=report_pk)
        queryset = reversion.get_for_object(report)
        version = queryset.get(pk=version_pk)
        # versions_pks = list(queryset.order_by('-pk').values_list(
        # 'pk', flat=True))

        # index = versions_pks.index(version.pk)

        with reversion.create_revision():
            version.revert()
            reversion.set_comment('Reverted')

        return HttpResponseRedirect(reverse_lazy('reports'))


class ISOCalendarView(TemplateView):
    page_title = _('ISO week calendars')
    template_name = 'webapp/calendar_with_week_numbers.html'
    name = 'iso_calendar'


class PdfFormListView(ListView):
    context_object_name = 'pdf_forms'
    page_title = _('PDF Forms')
    paginate_by = settings.PAGE_SIZE
    queryset = PdfForms.objects.all()
    template_name = 'webapp/pdf_list.html'
