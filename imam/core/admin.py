# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'www.grillazz.com'

from django.contrib import admin
from django.contrib.admin import site
import adminactions.actions as actions
from .models import Personnel, Program, Item, ProgramReport#, LowStockAlert

# register all adminactions
site.add_action(actions.export_as_fixture)
site.add_action(actions.export_as_csv)
site.add_action(actions.mass_update)


class personelAdmin(admin.ModelAdmin, ):
    list_display = ('name', 'site', 'position', 'mobile', 'email', )
admin.site.register(Personnel, personelAdmin)

class programAdmin(admin.ModelAdmin,):
    list_display = ('description', 'code', 'category', )
admin.site.register(Program, programAdmin)

class itemAdmin(admin.ModelAdmin,):
    list_display = ('description', 'code', 'unit', )
admin.site.register(Item, itemAdmin)

class programReportAdmin(admin.ModelAdmin,):
    list_display = ('site', 'program', 'report_date', )
admin.site.register(ProgramReport, programReportAdmin)

"""
class lowStockAlertAdmin(admin.ModelAdmin):
    list_display = ('site', 'item',)
admin.site.register(lowStockAlertAdmin,LowStockAlert)
"""
