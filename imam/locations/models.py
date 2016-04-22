# encoding=utf-8
from datetime import date
import logging

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.gis.db import models as geomodels
from django_extensions.db import fields as ext_fields
from django.utils.encoding import smart_text, python_2_unicode_compatible
from django.utils.translation import ugettext as _

from core.models import LocationProgramState, ProgramReport


_logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class LocationType(models.Model):
    code = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=75, blank=True, null=True)
    alt_names = models.CharField(max_length=75, blank=True, null=True)

    @classmethod
    def root(cls):
        obj = None
        try:
            obj = cls.objects.get(code='adm0')
        except cls.DoesNotExist:
            pass

        return obj

    @classmethod
    def get_site_type(cls):
        obj = None
        try:
            obj = cls.objects.get(code='adm6')
        except cls.DoesNotExist:
            pass

        return obj

    def __str__(self):
        return smart_text(self.name)

    class Meta:
        verbose_name = 'Location Type'


@python_2_unicode_compatible
class Location(MPTTModel):
    """Core Location model

    HP - Health Post (POSTO DE SAÚDE POS)
    OTHER - Other Clinic/TB treatment center (DISPENSÁRIO ANTI TUBERCULOSE
            OUTRO)
    CH - Central Hospital - Pediatric, Mental, Provincial Hospital (HOSPITAL
        CENTRAL HP)
    HOS - Hospital
    MH - Mental Hospital (Special Hospital HN/HC)
    MC - Maternity Center (CENTRO MATERNO INFANTIL CMI)
    HC - Health Center (CENTRO DE SAÚDE CEN)
    WH - Warehouse
    """

    FACTYPES = (
        ('HP', _('Health Post')),
        ('MH', _('Mental Hospital')),
        ('MC', _('Maternity Center')),
        ('HC', _('Health Center')),
        ('CH', _('Central Hospital')),
        ('HOS', _('Hospital')),
        ('WH', _('Warehouse')),
        ('OTHER', _('Other')),
    )
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')
    name = models.CharField(max_length=100, default=_('Unknown Name'))
    alt_names = models.CharField(
        max_length=150, blank=True, null=True,
        help_text=_('List of Alternate Place Names separated by (|)')
    )
    hcid = models.CharField(max_length=16, db_index=True, null=True,
                            unique=True, blank=True,
                            help_text='Unique ID: AABBCC##')
    srcid = models.CharField(
        max_length=75, db_index=True, blank=True, null=True,
        help_text=_('Code provided from source agency. HASC for GADM shapes.')
    )
    loc_type = models.ForeignKey(LocationType)
    fac_type = models.CharField(max_length=5, choices=FACTYPES, null=True,
                                blank=True)

    slug = ext_fields.AutoSlugField(populate_from='hcid', unique=True,
                                    max_length=16)
    uuid = ext_fields.UUIDField()
    created_at = ext_fields.CreationDateTimeField()
    updated_at = ext_fields.ModificationDateTimeField()

    class MPTTMeta:
        order_insertion_by = ['hcid']

    @classmethod
    def root(cls):
        obj = None
        root_loc_type = LocationType.root()
        try:
            obj = cls.objects.get(loc_type=root_loc_type)
        except cls.DoesNotExist:
            pass

        return obj

    @classmethod
    def get_by_code(cls, code):
        obj = None

        try:
            obj = cls.objects.get(hcid__iexact=code)
        except cls.DoesNotExist:
            return obj

        return obj

    @classmethod
    def get_sites(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()

        site_type = LocationType.get_site_type()

        if site_type is None:
            _logger.warning('No code for the site location type defined.')
            return []
        else:
            return queryset.filter(loc_type=site_type)

    def get_site_descendants(self):
        sites = Location.get_sites(self.get_descendants(True))
        return sites

    def active_site_count(self, program, year):
        sites = self.get_site_descendants()
        if year is None or year == date.today().year:
            return LocationProgramState.objects.filter(
                program=program, site__in=sites,
                current_state__startswith='ACTIVE'
            ).count()
        else:
            return ProgramReport.objects.filter(
                program=program, report_date__year=year, site__in=sites
            ).order_by('site').distinct('site').count()

    def inactive_site_count(self, program, year):
        sites = self.get_site_descendants()
        if year is None or year == date.today().year:
            return LocationProgramState.objects.filter(
                program=program, site__in=sites,
                current_state__startswith='INACTIVE').count()
        else:
            return self.reporting_site_count(program,
                                             year) - self.active_site_count(
                program, year)

    def reporting_site_count(self, program, year):
        sites = self.get_site_descendants()
        if year is None or year == 0 or year == date.today().year:
            return LocationProgramState.objects.filter(
                program=program, site__in=sites).exclude(
                current_state='OUT').count()
        else:
            return ProgramReport.objects.filter(
                program=program,
                report_date__lte='{:04d}-12-31'.format(year),
                site__in=sites
            ).order_by('site').distinct('site').count()

    @classmethod
    def get_location_choices(cls, type_code_exclude_list=None):
        qs = cls.objects.select_related('loc_type')

        if type_code_exclude_list:
            qs = qs.exclude(loc_type__code__in=type_code_exclude_list)

        displayed_locations = qs.values('pk', 'name', 'loc_type__name')
        filter_locations = {}
        for loc_data in displayed_locations:
            filter_locations.setdefault(loc_data['loc_type__name'], []).append(
                (loc_data['pk'], loc_data['name']))

        return [['', '']] + [[loc_type, filter_locations[loc_type]] for loc_type
                             in filter_locations.keys()]

    def __str__(self):
        return smart_text(self.name)

    def __unicode__(self):
        return self.__str__

    @property
    def location_breadcrumb(self):
        return ' > '.join(
            str(loc.name) for loc in self.get_ancestors(include_self=True))

    def location_path(self, include_self=False):
        path = list(
            self.get_ancestors(include_self).values_list('name', flat=True))
        path.reverse()
        return ', '.join(path[:-1])

    @property
    def geom(self):
        try:
            return self.location_gadm.geom
        except Gadm.DoesNotExist:
            try:
                return self.location_pnt.geom
            except SiteLocation.DoesNotExist:
                return None

    @property
    def is_site(self):
        site_type = LocationType.get_site_type()
        return self.loc_type == site_type

    @property
    def printable_programmes(self):
        return ', '.join(self.site_programs.values_list(
            'description', flat=True)
        )


@python_2_unicode_compatible
class Gadm(geomodels.Model):
    cc = geomodels.CharField(max_length=15, null=True, blank=True)
    engtype = geomodels.CharField(max_length=50, null=True, blank=True)
    loctype = geomodels.CharField(max_length=50, null=True, blank=True)
    hasc = geomodels.CharField(max_length=15, null=True, blank=True)
    id_0 = geomodels.IntegerField(null=True, blank=True)
    id_1 = geomodels.IntegerField(null=True, blank=True)
    id_2 = geomodels.IntegerField(null=True, blank=True)
    id_3 = geomodels.IntegerField(null=True, blank=True)
    srcid = geomodels.IntegerField(null=True, blank=True)
    iso = geomodels.CharField(max_length=3, null=True, blank=True)
    name = geomodels.CharField(max_length=75, null=True, blank=True)
    name_0 = geomodels.CharField(max_length=75, null=True, blank=True)
    name_1 = geomodels.CharField(max_length=75, null=True, blank=True)
    name_2 = geomodels.CharField(max_length=75, null=True, blank=True)
    name_3 = geomodels.CharField(max_length=75, null=True, blank=True)
    nl_name = geomodels.CharField(max_length=50, null=True, blank=True)
    remark = geomodels.CharField(max_length=125, null=True, blank=True)
    shape_area = geomodels.FloatField()
    shape_leng = geomodels.FloatField()
    validfr = geomodels.CharField(max_length=25, null=True, blank=True)
    validto = geomodels.CharField(max_length=25, null=True, blank=True)
    varname = geomodels.CharField(max_length=150, null=True, blank=True)

    location = geomodels.OneToOneField(Location, blank=True, null=True,
                                       related_name='location_gadm')

    geom = geomodels.MultiPolygonField(srid=4326)
    objects = geomodels.GeoManager()

    def save(self, *args, **kwargs):
        self.full_clean()  # performs regular validation then clean()
        super(Gadm, self).save(*args, **kwargs)

    def clean(self):
        if self.name:
            self.name = smart_text(self.name.strip())

    def __str__(self):
        return smart_text(self.name)

    class Meta:
        verbose_name = _('GADM Administrative Boundaries')
        verbose_name_plural = _('GADM Administrative Boundaries')


@python_2_unicode_compatible
class SiteLocation(geomodels.Model):
    code = geomodels.IntegerField(null=True)
    factype = geomodels.CharField(max_length=80, null=True, blank=True)
    name = geomodels.CharField(max_length=80, null=True, blank=True)
    altname = geomodels.CharField(max_length=80, null=True, blank=True)
    adm1_name = geomodels.CharField(max_length=80, null=True, blank=True)
    adm1_code = geomodels.IntegerField(null=True)
    adm2_name = geomodels.CharField(max_length=80, null=True, blank=True)
    adm2_code = geomodels.IntegerField(null=True)
    longitude = geomodels.FloatField(null=True)
    latitude = geomodels.FloatField(null=True)
    zonetype = geomodels.CharField(max_length=80, null=True, blank=True)
    nutrition = geomodels.CharField(max_length=80, null=True, blank=True)

    location = geomodels.OneToOneField(Location, blank=True, null=True,
                                       related_name='location_pnt')

    geom = geomodels.PointField(srid=4326)
    objects = geomodels.GeoManager()

    def save(self, *args, **kwargs):
        self.full_clean()  # performs regular validation then clean()
        super(SiteLocation, self).save(*args, **kwargs)

    def clean(self):
        if self.name:
            self.name = smart_text(self.name.strip())

    def __str__(self):
        return smart_text(self.name)

    class Meta:
        verbose_name = _('Health Site')
        verbose_name_plural = _('Health Sites')
