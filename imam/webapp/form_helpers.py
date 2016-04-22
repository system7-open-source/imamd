from django.core.urlresolvers import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout
from crispy_forms.bootstrap import FormActions


def make_base_program_report_filter_form_helper():
    # lay out the filter form
    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_action = reverse_lazy('reports')
    helper.layout = Layout(
        Fieldset(
            '',
            # 'Filter source records',
            Field('location'),
            Field('year'),
            Field('program'),
            FormActions(
                HTML(
                    '<button class="btn btn-warning form-submit" '
                    'data-dismiss="modal" aria-hidden="true"><i '
                    'class="icon-filter"></i> Filter</button>'
                ),
                HTML(
                    '<a class="btn form-reset" data-dismiss="modal" '
                    'aria-hidden="true">Reset</a>'
                ),
            )
        )
    )
    return helper


def make_program_report_filter_form_helper():
    helper = make_base_program_report_filter_form_helper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-4'
    helper.field_class = 'col-sm-8'
    return helper


def make_stock_filter_form_helper():
    helper = FormHelper()
    helper.form_action = reverse_lazy('stock_reports')
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-4'
    helper.field_class = 'col-sm-8'
    helper.form_method = 'post'
    helper.layout = Layout(
        Fieldset(
            '',
            # 'Filter source records',
            Field('location'),
            Field('start', placeholder='dd/mm/yyyy'),
            Field('end', placeholder='dd/mm/yyyy'),
            FormActions(
                HTML(
                    '<button class="btn btn-warning form-submit" '
                    'data-dismiss="modal" aria-hidden="true">'
                    '<i class="icon-filter"></i> Filter</button>'
                ),
                HTML(
                    '<a class="btn form-reset" data-dismiss="modal" '
                    'aria-hidden="true">Reset</a>'
                ),
            )
        )
    )

    return helper


def make_site_filter_form_helper():
    helper = FormHelper()
    helper.form_action = reverse_lazy('sites')
    helper.form_class = 'form-horizontal'
    helper.form_method = 'post'
    helper.layout = Layout(
        Fieldset(
            '',
            # 'Filter displayed sites',
            Field('location'),
            FormActions(
                HTML(
                    '<button class="btn btn-warning form-submit" '
                    'data-dismiss="modal" aria-hidden="true">'
                    '<i class="icon-filter"></i> Filter</button>'
                ),
                HTML(
                    '<a class="btn form-reset" data-dismiss="modal" '
                    'aria-hidden="true">Reset</a>'
                ),
            )
        )
    )

    return helper


def make_personnel_filter_form_helper():
    helper = FormHelper()
    helper.form_action = reverse_lazy('personnel')
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-4'
    helper.field_class = 'col-sm-8'
    helper.form_method = 'post'
    helper.layout = Layout(
        Fieldset(
            '',
            # 'Filter personnel',
            Field('location'),
            Field('position'),
            FormActions(
                HTML(
                    '<button class="btn btn-warning form-submit" '
                    'data-dismiss="modal" aria-hidden="true">'
                    '<i class="icon-filter"></i> Filter</button>'
                ),
                HTML(
                    '<a class="btn form-reset" data-dismiss="modal" '
                    'aria-hidden="true">Reset</a>'
                ),
            )
        )
    )

    return helper
