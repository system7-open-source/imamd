#!/usr/bin/env python
# encoding=utf-8

from django.conf.urls import patterns, include, url
from tastypie.api import Api
from .api.resources import Adm1Resource, Adm2Resource, Adm3Resource, FacilitiesResource
from .views import IndexView, LookupView#, Gmap3View, map_view

v1_api = Api(api_name='v1')
v1_api.register(Adm1Resource())
# v1_api.register(Adm2Resource())
# v1_api.register(Adm3Resource())
v1_api.register(FacilitiesResource())


urlpatterns = patterns(
    '',
    url(r'^/?$', IndexView.as_view(), name="locations_map"),
    url(r'^find/?$', LookupView.as_view(), name='locations_find'),
    url(r'^api/', include(v1_api.urls)),
)
