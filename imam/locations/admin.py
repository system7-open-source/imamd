#!/usr/bin/env python
# encoding=utf-8

from django.contrib.gis import admin as geoadmin
from django.contrib import admin

from .models import Location, LocationType, Gadm, SiteLocation


class GadmAdmin(geoadmin.OSMGeoAdmin):
    list_display = (
        'name', 'name_0', 'name_1', 'name_2', 'name_3', 'cc', 'hasc',
        'loctype', 'engtype', 'varname', 'srcid'
    )
    list_filter = ('loctype',)
    search_fields = ('srcid',)


class SiteLocationAdmin(geoadmin.OSMGeoAdmin):
    list_display = (
        'name', 'code', 'adm1_name', 'adm2_name', 'factype', 'location'
    )
    list_filter = ('factype',)
    search_fields = ('code',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'parent', 'hcid', 'srcid', 'loc_type', 'fac_type', 'alt_names'
    )
    list_filter = ('loc_type', 'fac_type')
    search_fields = ('srcid', 'hcid')


admin.site.register(LocationType, admin.ModelAdmin)
admin.site.register(Gadm, GadmAdmin)
admin.site.register(SiteLocation, SiteLocationAdmin)
admin.site.register(Location, LocationAdmin)
