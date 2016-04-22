#!/usr/bin/env python
# encoding=utf-8

import json

from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View, TemplateView
from django.http import JsonResponse

from core.models import LocationProgramState
from models import Location


class IndexView(TemplateView):
    """Main Locations Map UI"""
    page_title = _('Sites')
    template_name = 'locations-index.html'

    def get_context_data(self, **kwargs):
        facs = LocationProgramState.objects.exclude(
            current_state='OUT').exclude(
            site__location_pnt=None).select_related('site')

        facs_list = list()

        for f in facs:
            facs_list.append(
                {'name': f.site.name, 'alt_names': f.site.alt_names,
                 'hcid': f.site.hcid, 'srcid': f.site.srcid,
                 'slug': f.site.slug, 'fac_type': f.site.fac_type,
                 'geom': {'type': 'Point',
                          'coordinates': [f.site.location_pnt.geom.x,
                                          f.site.location_pnt.geom.y]}})

        js_facs_data = json.dumps(facs_list)

        return {
            'page_title': self.page_title,
            'facilities': js_facs_data
        }


class LookupView(View):
    """View class for Location lookup filter"""

    @staticmethod
    def get(request):
        ds = []
        if 'pk' in request.GET:
            try:
                pk = int(request.GET['pk'])
            except ValueError:
                pk = 1
            # If there is no location return an empty string, otherwise return
            # the location name.
            ds = Location.objects.filter(pk=pk).first()
            if isinstance(ds, Location):
                ds = ds.name
            else:
                ds = u''
        elif 'q' in request.GET:
            q = request.GET['q']
            ds = list(
                Location.objects.filter(name__icontains=q).order_by(
                    'loc_type__code', 'name'
                ).values_list(
                    'pk', 'name', 'loc_type__name'
                )[:37]
            )

        return JsonResponse(ds, safe=False)
