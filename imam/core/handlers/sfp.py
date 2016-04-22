from __future__ import unicode_literals
from itertools import izip_longest
from django.utils.translation import ugettext_lazy as _
import reversion

from .base import BaseHandler
from ..forms import ProgramReportForm
from ..models import Program, ProgramReport
from locations.models import Location


# group codes to exclude from report
EXCLUDE_GROUP_CODES = ['05']


class SFPReportHandler(BaseHandler):
    fields = ['group_code', 'period_spec', 'new_marasma_admissions',
              'new_relapsed_admissions', 'transfers_in', 'cures', 'deaths',
              'unconfirmed_defaults', 'non_responses', 'transfers_out',
              'site_id']
    form_class = ProgramReportForm
    help_text = _('Please consult the job aid for message format')
    program_code = 'SFP'

    def parse_message(self, text):
        words = text.upper().split()

        location = Location.get_by_code(words[-1])
        if location:
            location_code = words.pop()
        else:
            location_code = None

        parsed = dict(izip_longest(self.fields, words))
        if location_code:
            parsed['site_id'] = location_code

        return parsed

    def process_params(self, params):
        site = params.get('site')
        group = params.get('group')
        program = Program.get_by_code(self.program_code)
        period_spec = params.get('period_spec')

        if group.code in EXCLUDE_GROUP_CODES:
            return _('Report not allowed for {group}').format(
                group=group.description)

        report = ProgramReport.get_report(period_spec, group, program, site)

        if report is None:
            report = ProgramReport.make_blank_report(period_spec)
            report.group = group
            report.site = site
            report.program = program

        with reversion.create_revision():
            report.reporter = params.get('reporter')
            report.new_marasmic_patients = params.get('new_marasmic_patients')
            report.new_oedema_patients = params.get('new_oedema_patients')
            report.new_relapsed_patients = params.get('new_relapsed_patients')
            report.hiv_positive_patients = params.get('hiv_positive_patients')
            report.readmitted_patients = params.get('readmitted_patients')
            report.patients_transferred_in = params.get(
                'patients_transferred_in')
            report.patients_transferred_out = params.get(
                'patients_transferred_out')
            report.patient_deaths = params.get('patient_deaths')
            report.confirmed_patient_defaults = params.get(
                'confirmed_patient_defaults')
            report.unconfirmed_patient_defaults = params.get(
                'unconfirmed_patient_defaults')
            report.unresponsive_patients = params.get('unresponsive_patients')
            report.patients_cured = params.get('patients_cured')

            prior_report = report.prior_report

            if prior_report:
                report.patients_at_period_start =\
                    prior_report.patients_at_period_end
            report.save()

            summary = report.summary()

            if report.reporter.user:
                reversion.set_user(report.reporter.user)
            reversion.set_comment('Updated via SMS')

        return _(
            'Thank you {name}. For {period_name} there were {Atot} new '
            'admissions, {Dcur} cures, {Dead} deaths, {DefT} defaults, {Dmed} '
            'no response and {Tout} transfers from {SiteName}.'
        ).format(**summary)
