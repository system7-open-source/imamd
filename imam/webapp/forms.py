from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Fieldset, Field, HTML, Submit
from crispy_forms.bootstrap import FormActions

from locations.models import Location
from core.models import ProgramReport


class SiteCreateForm(forms.Form):
    parent = forms.ChoiceField(
        choices=Location.get_location_choices(['adm0', 'adm6']), label='Parent')
    name = forms.CharField(label='Name')
    hcid = forms.CharField(label='Site ID')
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Create new site',
                Field('parent', css_class='select-two'),
                'name',
                'hcid',
                'latitude',
                'longitude'
            ),
            FormActions(
                HTML('<button class="btn btn-primary">Create</button>')
            )
        )
        super(SiteCreateForm, self).__init__(*args, **kwargs)

    def clean_hcid(self):
        hcid = self.cleaned_data['hcid']

        loc = Location.get_by_code(hcid)

        if loc:
            raise forms.ValidationError(_('Site ID is already in use'))

        return hcid

    def clean_parent(self):
        parent_pk = self.cleaned_data['parent']

        try:
            parent = Location.objects.get(pk=parent_pk)
        except Location.DoesNotExist:
            raise forms.ValidationError(_('Invalid parent'))

        self.cleaned_data['parent_loc'] = parent

        return parent_pk


class ProgramReportForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Edit {{ program }} report for {{ period }}',
                Div(HTML(
                    '<span class="uneditable-input">Reported by: {{ '
                    'reporter.name }}</span>'),
                    css_class='control-group'),
                'period_number',
                Field('group', css_class='select-two'),
                'new_marasmic_patients',
                'patients_transferred_in',
                'patients_cured',
                'patient_deaths',
                'unconfirmed_patient_defaults',
                'unresponsive_patients',
                'patients_transferred_out',
                'comment'
            ),
            FormActions(
                Submit('submit', 'Save', css_class='btn btn-primary'),
            )
        )
        super(ProgramReportForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['period_number', 'group', 'new_marasmic_patients',
                  'patients_transferred_in', 'patients_cured', 'patient_deaths',
                  'unconfirmed_patient_defaults', 'unresponsive_patients',
                  'patients_transferred_out']
        model = ProgramReport
