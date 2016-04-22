import calendar
from tastypie.resources import ModelResource
from rapidsms.contrib.messagelog.models import Message


class MessageResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        excludes = ['pk', 'id']
        queryset = Message.objects.all().order_by('-pk')
        resource_name = 'messages'

    def dehydrate(self, bundle):
        bundle.data['phone'] = bundle.obj.connection.identity
        bundle.data['date'] = calendar.timegm(bundle.obj.date.utctimetuple())
        bundle.data['direction'] = bundle.obj.get_direction_display()
        return bundle
