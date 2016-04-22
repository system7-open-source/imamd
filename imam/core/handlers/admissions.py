from __future__ import unicode_literals
from itertools import izip_longest
from django.utils.translation import ugettext_lazy as _
from .base import BaseHandler
from ..forms import AdmissionValidationForm
from ..models import ProgramReport


class AdmissionValidationHandler(BaseHandler):
    fields = ['site_id', 'report_type_spec', 'group_code', 'period_spec']
    form_class = AdmissionValidationForm
    help_text = _('Send {prefix} {keyword} SITE-ID REPORT-TYPE GROUP-CODE PERIOD')
    keyword = 'adm'

    def parse_message(self, text):
        words = text.lower().split()
        parsed = dict(izip_longest(self.fields, words))
        return parsed

    def process_params(self, params):
        group = params.get('group')
        program = params.get('program')
        site = params.get('site')
        period_spec = params.get('period_spec')
        report = None

        if period_spec:
            report = ProgramReport.get_report(period_spec, group, program, site)
        else:
            try:
                report = ProgramReport.objects.filter(group__pk=group.pk, site__pk=site.pk, program__pk=program.pk).latest()
            except ProgramReport.DoesNotExist:
                pass

        if report is None:
            return _('There are no reports for {site_id}').format(site_id=site.hcid)

        summary = report.summary()
        return _('For {period_name} there were {Atot} new admissions, {Dcur} cures, {Dead} deaths, {DefT} defaults,' \
            '{Dmed} no response, {Tout} transfers and {End} under Rx at {SiteName}.').format(**summary)
