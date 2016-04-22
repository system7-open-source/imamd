# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'www.grillazz.com'

from .models import PdfForms
from django.contrib import admin
from django.contrib.admin import site
import adminactions.actions as actions

# register all adminactions
site.add_action(actions.export_as_fixture)
site.add_action(actions.export_as_csv)

class pdfFormsAdmin(admin.ModelAdmin, ):
    list_display = ('formName',)
    prepopulated_fields = {'slug': ['formName']}
admin.site.register(PdfForms, pdfFormsAdmin)

