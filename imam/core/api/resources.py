import calendar
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL_WITH_RELATIONS
from locations.models import Location
from core.models import LowStockAlert, ProgramReport, StockOutReport, Program


class ProgramReportResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        queryset = ProgramReport.objects.all()

class ProgramResource(ModelResource):
    class Meta:
        resource_name = 'program'
        allowed_methods = ['get']
        queryset = Program.objects.all()
        filtering = {
            "code": ALL_WITH_RELATIONS,
        }

class StockOutResource(ModelResource):
    items = fields.CharField()

    class Meta:
        allowed_methods = ['get']
        exclude = ['pk', 'created', 'modified']
        queryset = StockOutReport.objects.all()
        resource_name = 'stockouts'
        filtering = {
            'created': ('exact', 'lte', 'gte'),
            'location': ('under'),
        }

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(StockOutResource, self).build_filters(filters)

        if 'location' in filters:
            value = filters['location']

            if value:
                try:
                    location = Location.objects.get(pk=value)
                    descendant_site_pks = Location.get_sites(location.get_descendants()).values_list('pk', flat=True)
                except Location.DoesNotExist:
                    return orm_filters

                orm_filters['site__pk__in'] = descendant_site_pks

        return orm_filters

    def dehydrate(self, bundle):
        bundle.data['date'] = calendar.timegm(bundle.obj.modified.utctimetuple())
        bundle.data['items'] = bundle.obj.summary
        bundle.data['location'] = bundle.obj.site.name
        bundle.data['site_id'] = bundle.obj.site.hcid
        bundle.data['path'] = bundle.obj.site.location_path()

        return bundle


class LowStockResource(ModelResource):
    item = fields.CharField()

    class Meta:
        allowed_methods = ['get']
        exclude = ['pk', 'created', 'modified']
        queryset = LowStockAlert.objects.all()
        resource_name = 'low_stocks'

    def dehydrate(self, bundle):
        bundle.data['item'] = bundle.obj.item.code
        bundle.data['date'] = calendar.timegm(bundle.obj.modified.utctimetuple())
        bundle.data['location'] = bundle.obj.site.name
        bundle.data['site_id'] = bundle.obj.site.hcid
        bundle.data['path'] = bundle.obj.site.location_path()

        return bundle
