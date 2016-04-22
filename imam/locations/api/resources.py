#!/usr/bin/env python
# encoding=utf-8
from tastypie import fields
from tastypie.fields import CharField, IntegerField
from tastypie.resources import ModelResource
from tastypie.contrib.gis.resources import ModelResource as GeoModelResource
from tastypie.contrib.gis.resources import GeometryApiField
from tastypie.cache import SimpleCache, NoCache
from tastypie.constants import ALL_WITH_RELATIONS
# from imam.cachedresource import ClientCachedResource
from ..models import Location

from core.api.resources import ProgramResource
from core.models import LocationProgramState


class Adm1Resource(GeoModelResource):
    geom = GeometryApiField(attribute='geom')

    class Meta:
        limit = 0
        queryset = Location.objects.select_related('gadm').filter(loc_type__code="adm1")
        resource_name = 'adm1'
        allowed_methods = ['get']
        cache = NoCache()
        # 24 hours = 86400, 7 days = 604800, 4 weeks = 2419200
        # cache = SimpleCache(timeout=604800)
        # cache_control = {"max_age": 604800, "s_maxage": 2419200}


class Adm2Resource(GeoModelResource):
    geom = GeometryApiField(attribute='geom', readonly=True)

    class Meta:
        limit = 0
        queryset = Location.objects.select_related('gadm').filter(loc_type__code="adm2")
        resource_name = 'adm2'
        allowed_methods = ['get']
        cache = NoCache()
        # cache = SimpleCache(timeout=604800)
        # cache_control = {"max_age": 604800, "s_maxage": 2419200}


class Adm3Resource(GeoModelResource):
    # geom = GeometryApiField(attribute='geom', readonly=True)

    class Meta:
        limit = 0
        queryset = Location.objects.select_related('gadm').filter(loc_type__code="adm3")
        resource_name = 'adm3'
        allowed_methods = ['get']
        cache = NoCache()
        # cache = SimpleCache(timeout=604800)
        # cache_control = {"max_age": 604800, "s_maxage": 2419200}


class FacilitiesResource(GeoModelResource):
    geom = GeometryApiField(attribute='site__geom', readonly=True)
    program = fields.ForeignKey(ProgramResource, 'program', full=True)

    class Meta:
        #limit = 0
        queryset = LocationProgramState.objects.exclude(current_state='OUT').exclude(site__location_pnt=None)
        resource_name = 'facilities'
        allowed_methods = ['get']
        #cache = NoCache()
        filtering = {
            'program': ALL_WITH_RELATIONS,
            }
        # cache = SimpleCache(timeout=86400)
        # cache_control = {"max_age": 86400, "s_maxage": 86400}


    def dehydrate(self, bundle):
        bundle.data['name'] = bundle.obj.site.name
        bundle.data['hcid'] = bundle.obj.site.hcid
        return bundle

class NonSiteLocationNameResource(ModelResource):
    loc_type = CharField()
    parent_id = IntegerField()
    text = CharField()

    class Meta:
        fields = ['pk']
        limit = 0
        resource_name = 'location-names'
        allowed_methods = ['get']
        queryset = Location.objects.exclude(loc_type__code='adm6')

    def dehydrate(self, bundle):
        bundle.data['text'] = bundle.obj.name
        bundle.data['loc_type'] = bundle.obj.loc_type.name.lower()
        if bundle.obj.parent:
            bundle.data['parent_id'] = bundle.obj.parent.pk
        else:
            bundle.data['parent_id'] = None

        return bundle
