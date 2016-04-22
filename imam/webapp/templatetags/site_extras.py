from django import template

from locations.models import LocationType


register = template.Library()

excluded_codes = ['adm3', 'adm4', 'adm5']
# added -1 because location type code counts begin from 0
max_size = LocationType.objects.count() - len(excluded_codes) - 1


@register.filter('list_ancestors')
def list_ancestors(queryset):
    size = queryset.count()
    ancestors = list(drop_unused(queryset))
    ancestors.extend([None] * (max_size - size))

    return ancestors


def drop_unused(queryset):
    return queryset.exclude(loc_type__code__in=excluded_codes)


@register.filter('remove_unused_location_types')
def remove_unused_location_types(queryset):
    return queryset.exclude(code__in=excluded_codes)
