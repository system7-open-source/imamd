from __future__ import unicode_literals
from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from locations.models import Location
from .models import Item, PatientGroup, Position, Program, ProgramReport

PROGRAM_MAP = {'i': 'IPF', 'o': 'OTP', 'm': 'SFP'}


class FormErrorList(ErrorList):

    '''SMS-specific subclass of ErrorList'''
    def as_text(self):
        '''Returns errors as a single string'''
        if not self:
            return ''
        return ''.join(['%s' % force_unicode(e) for e in self])


class HandlerForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop('connection', None)
        kwargs['error_class'] = FormErrorList
        super(HandlerForm, self).__init__(*args, **kwargs)

    def error(self):
        errors = self.errors
        error = None
        if self.errors:
            for field in self.fields:
                if field in errors:
                    error = errors[field].as_text()
                    break
            if error is None and NON_FIELD_ERRORS in errors:
                error = errors[NON_FIELD_ERRORS].as_text()

        return error

    def save(self):
        self.cleaned_data['connection'] = self.connection
        return self.cleaned_data


class RegistrationForm(HandlerForm):
    site_id = forms.CharField()
    name = forms.CharField(error_messages={
        'required': _('Your registration SMS contains errors. Format SMS as REG SITE-ID Name Lastname Position Email')
    })
    position_code = forms.CharField(error_messages={
        'required': _('Your registration SMS contains errors. Format SMS as REG SITE-ID Name Lastname Position Email')
    })
    email = forms.EmailField(required=False)

    def clean_site_id(self):
        site_id = self.cleaned_data['site_id']

        location = Location.get_by_code(site_id)
        if not location:
            raise forms.ValidationError(_(
                'The site ID you entered does not exist - are you missing one or more zeros? Please try again.'))

        self.cleaned_data['site'] = location
        return site_id

    def clean_position_code(self):
        position_code = self.cleaned_data['position_code']
        position = Position.get_by_code(position_code)
        if not position:
            raise forms.ValidationError(_(
                'The position you entered does not exist. Please check job aid and resend.'))

        self.cleaned_data['position'] = position
        return position_code

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        position = cleaned_data.get('position')
        site = cleaned_data.get('site')

        if not position or not site:
            return cleaned_data

        if position.loc_type:
            if position.loc_type != site.loc_type:
                raise forms.ValidationError(_('You cannot register at that location'))

        return cleaned_data


class AdmissionValidationForm(HandlerForm):
    site_id = forms.CharField()
    report_type_spec = forms.CharField()
    group_code = forms.CharField()
    period_spec = forms.CharField(required=False)

    def clean(self):
        if not self.connection.contact:
            raise forms.ValidationError(_(
                'You are not registered in the system. Please register using the command REG.'))

        return super(AdmissionValidationForm, self).clean()

    def clean_site_id(self):
        site_id = self.cleaned_data.get('site_id')

        if site_id:
            site = Location.get_by_code(site_id)
            if not site:
                raise forms.ValidationError(_(
                    'Error in site ID - are you missing one or more zeros? Please enter or correct the site ID and resend.'))
        else:
            site = self.connection.contact.worker.site

        if not site.is_site:
            raise forms.ValidationError(_(
                'Error in site ID. Please enter or correct the site ID and resend.'))

        # Nigeria-specific site ID check to prevent validation of
        # admissions at warehouses
        if not site.hcid.isdigit():
            raise forms.ValidationError(_(
                'Error in site ID. Please enter or correct the site ID and resend.'))

        worker = self.connection.contact.worker
        if not worker.site.is_ancestor_of(site, include_self=True):
            raise forms.ValidationError(_(
                'Error in site ID. Please enter or correct the site ID and resend.'))

        self.cleaned_data['site'] = site
        self.cleaned_data['reporter'] = worker
        return site_id

    def clean_report_type_spec(self):
        report_type_spec = self.cleaned_data.get('report_type_spec')
        period_code, program_code = report_type_spec[:2]

        if program_code not in PROGRAM_MAP:
            raise forms.ValidationError(
                'Error in command. Please check job aid and resend.')

        self.cleaned_data['program'] = Program.get_by_code(
            PROGRAM_MAP[program_code])

        return report_type_spec

    def clean_group_code(self):
        group_code = self.cleaned_data.get('group_code')
        group = PatientGroup.get_by_code(group_code)
        if not group:
            raise forms.ValidationError(_(
                'Error in command. Please check job aid and resend.'))

        self.cleaned_data['group'] = group
        return group_code

    def clean_period_spec(self):
        period_spec = self.cleaned_data.get('period_spec')

        if period_spec:
            result = ProgramReport._validate_period_spec(period_spec)
            if not result:
                raise forms.ValidationError(_(
                    'Error in reporting period. Please check the format for report period and resend.'))

        return period_spec


class ProgramReportForm(HandlerForm):
    group_code = forms.CharField()
    period_spec = forms.CharField()
    new_marasma_admissions = forms.CharField()
    new_oedema_admissions = forms.CharField(required=False)
    new_relapsed_admissions = forms.CharField(required=False)
    hiv_positive_admissions = forms.CharField(required=False)
    readmissions = forms.CharField(required=False)
    transfers_in = forms.CharField(required=False)
    transfers_out = forms.CharField(required=False)
    deaths = forms.CharField(required=False)
    confirmed_defaults = forms.CharField(required=False)
    unconfirmed_defaults = forms.CharField(required=False)
    non_responses = forms.CharField(required=False)
    cures = forms.CharField(required=False)
    site_id = forms.CharField(required=False)

    def clean(self):
        if not self.connection.contact:
            raise forms.ValidationError(_(
                'You are not registered in the system. Please register using the command REG.'))

        return super(ProgramReportForm, self).clean()

    def clean_group_code(self):
        group_code = self.cleaned_data.get('group_code')
        group = PatientGroup.get_by_code(group_code)
        if not group:
            raise forms.ValidationError(_(
                'Error in command. Please check job aid and resend.'))

        self.cleaned_data['group'] = group
        return group_code

    def clean_period_spec(self):
        period_spec = self.cleaned_data.get('period_spec')
        result = ProgramReport._validate_period_spec(period_spec)
        if not result:
            raise forms.ValidationError(_(
                'Error in reporting period. Please check the format for report period and resend.'))

        return period_spec

    def clean_new_marasma_admissions(self):
        new_marasma_admissions = self.cleaned_data.get(
            'new_marasma_admissions')

        if new_marasma_admissions.lower() == 'x':
            self.cleaned_data['new_marasmic_patients'] = None
        else:
            try:
                self.cleaned_data['new_marasmic_patients'] = int(
                    new_marasma_admissions)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in anthropometry admission cell. Please correct the data entered in the SMS and resend.'))
        return new_marasma_admissions

    def clean_new_oedema_admissions(self):
        new_oedema_admissions = self.cleaned_data.get('new_oedema_admissions')

        if not new_oedema_admissions:
            self.cleaned_data['new_oedema_patients'] = None
            return new_oedema_admissions

        if new_oedema_admissions.lower() == 'x':
            self.cleaned_data['new_oedema_patients'] = None
        else:
            try:
                self.cleaned_data['new_oedema_patients'] = int(
                    new_oedema_admissions)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in oedema admissions cell. Please correct the data entered in the SMS and resend.'))
        return new_oedema_admissions

    def clean_new_relapsed_admissions(self):
        new_relapsed_admissions = self.cleaned_data.get(
            'new_relapsed_admissions')

        if not new_relapsed_admissions:
            self.cleaned_data['new_relapsed_patients'] = None
            return new_relapsed_admissions

        if new_relapsed_admissions.lower() == 'x':
            self.cleaned_data['new_relapsed_patients'] = None
        else:
            try:
                self.cleaned_data['new_relapsed_patients'] = int(
                    new_relapsed_admissions)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in relapsed cell. Please correct the data entered in the SMS and resend.'))
        return new_relapsed_admissions

    def clean_hiv_positive_admissions(self):
        hiv_positive_admissions = self.cleaned_data.get(
            'hiv_positive_admissions')

        if not hiv_positive_admissions:
            self.cleaned_data['hiv_positive_patients'] = None
            return hiv_positive_admissions

        if hiv_positive_admissions.lower() == 'x':
            self.cleaned_data['hiv_positive_patients'] = None
        else:
            try:
                self.cleaned_data['hiv_positive_patients'] = int(
                    hiv_positive_admissions)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in HIV+ admissions cell. Please correct the data entered in the SMS and resend.'))
        return hiv_positive_admissions

    def clean_readmissions(self):
        readmissions = self.cleaned_data.get('readmissions')

        if not readmissions:
            self.cleaned_data['readmitted_patients'] = None
            return readmissions

        if readmissions.lower() == 'x':
            self.cleaned_data['readmitted_patients'] = None
        else:
            try:
                self.cleaned_data['readmitted_patients'] = int(readmissions)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in readmissions cell. Please correct the data entered into the SMS and resend.'))
        return readmissions

    def clean_transfers_in(self):
        transfers_in = self.cleaned_data.get('transfers_in')

        if not transfers_in:
            self.cleaned_data['patients_transferred_in'] = None
            return transfers_in

        if transfers_in.lower() == 'x':
            self.cleaned_data['patients_transferred_in'] = None
        else:
            try:
                self.cleaned_data[
                    'patients_transferred_in'] = int(transfers_in)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in transfer in cell. Please correct the data entered in the SMS and resend.'))
        return transfers_in

    def clean_transfers_out(self):
        transfers_out = self.cleaned_data.get('transfers_out')

        if not transfers_out:
            self.cleaned_data['patients_transferred_out'] = None
            return transfers_out

        if transfers_out.lower() == 'x':
            self.cleaned_data['patients_transferred_out'] = None
        else:
            try:
                self.cleaned_data[
                    'patients_transferred_out'] = int(transfers_out)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in transfer out cell. Please correct the data entered in the SMS and resend.'))
        return transfers_out

    def clean_deaths(self):
        deaths = self.cleaned_data.get('deaths')

        if not deaths:
            self.cleaned_data['patient_deaths'] = None
            return deaths

        if deaths.lower() == 'x':
            self.cleaned_data['patient_deaths'] = None
        else:
            try:
                self.cleaned_data['patient_deaths'] = int(deaths)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in deaths cell. Please correct the data entered in the SMS and resend.'))
        return deaths

    def clean_confirmed_defaults(self):
        confirmed_defaults = self.cleaned_data.get('confirmed_defaults')

        if not confirmed_defaults:
            self.cleaned_data['confirmed_patient_defaults'] = None
            return confirmed_defaults

        if confirmed_defaults.lower() == 'x':
            self.cleaned_data['confirmed_patient_defaults'] = None
        else:
            try:
                self.cleaned_data['confirmed_patient_defaults'] = int(
                    confirmed_defaults)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in defaults cell. Please correct the data entered in the SMS and resend.'))
        return confirmed_defaults

    def clean_unconfirmed_defaults(self):
        unconfirmed_defaults = self.cleaned_data.get('unconfirmed_defaults')

        if not unconfirmed_defaults:
            self.cleaned_data['unconfirmed_patient_defaults'] = None
            return unconfirmed_defaults

        if unconfirmed_defaults.lower() == 'x':
            self.cleaned_data['unconfirmed_patient_defaults'] = None
        else:
            try:
                self.cleaned_data['unconfirmed_patient_defaults'] = int(
                    unconfirmed_defaults)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in defaults cell. Please correct the data entered in the SMS and resend.'))
        return unconfirmed_defaults

    def clean_non_responses(self):
        non_responses = self.cleaned_data.get('non_responses')

        if not non_responses:
            self.cleaned_data['unresponsive_patients'] = None
            return non_responses

        if non_responses.lower() == 'x':
            self.cleaned_data['unresponsive_patients'] = None
        else:
            try:
                self.cleaned_data['unresponsive_patients'] = int(non_responses)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in no response cell. Please correct the data entered in the SMS and resend.'))
        return non_responses

    def clean_cures(self):
        cures = self.cleaned_data.get('cures')

        if not cures:
            self.cleaned_data['patients_cured'] = None
            return cures

        if cures.lower() == 'x':
            self.cleaned_data['patients_cured'] = None
        else:
            try:
                self.cleaned_data['patients_cured'] = int(cures)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in cures cell. Please correct the data entered in the SMS and resend.'))
        return cures

    def clean_site_id(self):
        site_id = self.cleaned_data.get('site_id')

        if site_id:
            site = Location.get_by_code(site_id)
            if not site:
                raise forms.ValidationError(_(
                    'Error in site ID - are you missing one or more zeros? Please enter or correct the site ID and resend.'))
        else:
            site = self.connection.contact.worker.site

        if not site.is_site:
            raise forms.ValidationError(_(
                'Error in site ID. Please enter or correct the site ID and resend.'))

        # Nigeria-specific Site ID check
        if not site.hcid.isdigit():
            raise forms.ValidationError(_('Error in site ID. Please enter or correct the site ID and resend.'))

        worker = self.connection.contact.worker
        if not worker.site.is_ancestor_of(site, include_self=True):
            raise forms.ValidationError(_(
                'Error in site ID. Please enter or correct the site ID and resend.'))

        self.cleaned_data['site'] = site
        self.cleaned_data['reporter'] = worker
        return site_id


class OTPReportForm(ProgramReportForm):

    def clean_new_marasma_admissions(self):
        new_marasma_admissions = self.cleaned_data.get(
            'new_marasma_admissions')

        if new_marasma_admissions.lower() == 'x':
            self.cleaned_data['new_marasmic_patients'] = None
        else:
            try:
                self.cleaned_data['new_marasmic_patients'] = int(
                    new_marasma_admissions)
            except ValueError:
                raise forms.ValidationError(_(
                    'Error in anthropomety/oedema admission cell. Please correct the data entered in the SMS and resend.'))
        return new_marasma_admissions


class ItemForm(HandlerForm):
    item_code = forms.CharField()

    def clean_item_code(self):
        item_code = self.cleaned_data.get('item_code')
        item = Item.get_by_code(item_code)
        if not item:
            raise forms.ValidationError(_(
                '*Error in stock code* Please correct the stock codes entered in the SMS and resend.'))

        self.cleaned_data['item'] = item
        return item_code


class InventoryReportForm(ItemForm):
    last_receipt = forms.IntegerField(error_messages={
        'required': _('*Error in SMS format* Please check the job aid for the correct SMS format and resend.')
    })
    current_stock = forms.IntegerField(error_messages={
        'required': _('*Error in SMS format* Please check the job aid for the correct SMS format and resend.')
    })
