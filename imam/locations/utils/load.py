#!/usr/bin/env python
# encoding=utf-8

from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from django.utils.encoding import smart_text, python_2_unicode_compatible

from ..models import Location, Gadm, SiteLocation, LocationType


# ./manage.py ogrinspect apps/locations/data/CMR_adm/CMR_adm3.shp
#                               LocationGeoPoly --srid=4326 --mapping --multi
# ./manage.py dumpdata locations.location locations.locationgeopoly
#                                                               > nga_adm.json


def load_gadm(country, adm_shp, level):
    # Set Up Mappings and Links to SHP files
    adm0_mapping = {
        'id_0': 'GADMID',
        'srcid': 'GADMID',
        'iso': 'ISO',
        'name': 'NAME_ISO',
        'hasc': 'ISO2',
        'validfr': 'VALIDFR',
        'validto': 'VALIDTO',
        'shape_leng': 'Shape_Leng',
        'shape_area': 'Shape_Area',
        'geom': 'MULTIPOLYGON',
    }
    adm1_mapping = {
        'id_0': 'ID_0',
        'iso': 'ISO',
        'name_0': 'NAME_0',
        'id_1': 'ID_1',
        'srcid': 'ID_1',
        'name_1': 'NAME_1',
        'name': 'NAME_1',
        'varname': 'VARNAME_1',
        'nl_name': 'NL_NAME_1',
        'hasc': 'HASC_1',
        'cc': 'CC_1',
        'loctype': 'TYPE_1',
        'engtype': 'ENGTYPE_1',
        'validfr': 'VALIDFR_1',
        'validto': 'VALIDTO_1',
        'remark': 'REMARKS_1',
        'shape_leng': 'Shape_Leng',
        'shape_area': 'Shape_Area',
        'geom': 'MULTIPOLYGON',
    }
    adm2_mapping = {
        'id_0': 'ID_0',
        'iso': 'ISO',
        'name_0': 'NAME_0',
        'id_1': 'ID_1',
        'name_1': 'NAME_1',
        'id_2': 'ID_2',
        'srcid': 'ID_2',
        'name_2': 'NAME_2',
        'name': 'NAME_2',
        'varname': 'VARNAME_2',
        'nl_name': 'NL_NAME_2',
        'hasc': 'HASC_2',
        'cc': 'CC_2',
        'loctype': 'TYPE_2',
        'engtype': 'ENGTYPE_2',
        'validfr': 'VALIDFR_2',
        'validto': 'VALIDTO_2',
        'remark': 'REMARKS_2',
        'shape_leng': 'Shape_Leng',
        'shape_area': 'Shape_Area',
        'geom': 'MULTIPOLYGON',
    }
    adm3_mapping = {
        'id_0': 'ID_0',
        'iso': 'ISO',
        'name_0': 'NAME_0',
        'id_1': 'ID_1',
        'name_1': 'NAME_1',
        'id_2': 'ID_2',
        'name_2': 'NAME_2',
        'id_3': 'ID_3',
        'srcid': 'ID_3',
        'name_3': 'NAME_3',
        'name': 'NAME_3',
        'varname': 'VARNAME_3',
        'nl_name': 'NL_NAME_3',
        'hasc': 'HASC_3',
        'loctype': 'TYPE_3',
        'engtype': 'ENGTYPE_3',
        'validfr': 'VALIDFR_3',
        'validto': 'VALIDTO_3',
        'remark': 'REMARKS_3',
        'shape_leng': 'Shape_Leng',
        'shape_area': 'Shape_Area',
        'geom': 'MULTIPOLYGON',
    }

    if level == 0:
        import_gadm(DataSource(adm_shp), adm0_mapping)
    elif level == 1:
        import_gadm(DataSource(adm_shp), adm1_mapping)
    elif level == 2:
        import_gadm(DataSource(adm_shp), adm2_mapping)
    elif level == 3:
        import_gadm(DataSource(adm_shp), adm3_mapping)

    return True


@python_2_unicode_compatible
def import_gadm(adm_shp, adm_map):
    lm_adm = LayerMapping(Gadm, adm_shp, adm_map, transform=False,
                          encoding='utf-8')
    lm_adm.save(strict=True, verbose=False)

    return True


@python_2_unicode_compatible
def load_sites(sites_shp):
    sites_map = {
        'code': 'CODE',
        'factype': 'TYPE',
        'name': 'NAMEOFFICI',
        'altname': 'NAMEPOPULA',
        'adm1_name': 'PROVINCE',
        'adm1_code': 'PROVCODE',
        'adm2_name': 'MUNICIPALI',
        'adm2_code': 'MUNICODE',
        'longitude': 'LONGITUDE',
        'latitude': 'LATITUDE',
        'zonetype': 'ZONETYPE',
        'nutrition': 'NUTRITION',
        'geom': 'POINT',
    }

    lm_import = LayerMapping(SiteLocation, sites_shp, sites_map,
                             transform=False, encoding='utf-8')
    lm_import.save(strict=True, verbose=False)

    return True


@python_2_unicode_compatible
def gadm_to_loc(country_name):
    # create root country location (adm0)
    country_gadm = Gadm.objects.get(name=country_name)
    country_type = LocationType.objects.get(code='adm0')

    country_loc = Location.objects.create(
        name=smart_text(country_gadm.name.strip().title()),
        loc_type=country_type,
        hcid=country_gadm.hasc, srcid=country_gadm.srcid)
    country_gadm.location = country_loc
    country_gadm.save()

    # create provinces (adm1)
    provinces_gadm = Gadm.objects.filter(engtype="Province")
    province_type = LocationType.objects.get(code='adm1')

    for prov_gadm in provinces_gadm:
        prov_loc = Location.objects.create(
            name=smart_text(prov_gadm.name.strip().title()),
            loc_type=province_type,
            hcid=prov_gadm.hasc[3:], srcid=prov_gadm.srcid, parent=country_loc,
            alt_names=smart_text(prov_gadm.varname.strip()))
        prov_gadm.location = prov_loc
        prov_gadm.save()
        print u"1: %s" % prov_gadm.location

    # create municipalities (adm2)
    munis_gadm = Gadm.objects.filter(engtype="Municpality|City Council")
    muni_type = LocationType.objects.get(code='adm2')

    for muni_gadm in munis_gadm:
        hcid = muni_gadm.hasc[3:].replace(".", "")
        parent_loc = provinces_gadm.get(srcid=muni_gadm.id_1).location

        muni_loc = Location.objects.create(
            name=smart_text(muni_gadm.name.strip().title()), loc_type=muni_type,
            hcid=hcid, srcid=muni_gadm.srcid, parent=parent_loc,
            alt_names=smart_text(muni_gadm.varname.strip()))
        muni_gadm.location = muni_loc
        muni_gadm.save()
        print u"2: %s - %s" % (muni_gadm.location, muni_loc.hcid)

    # create communes (adm3)
    communes_gadm = Gadm.objects.filter(engtype="Commune")
    commune_type = LocationType.objects.get(code='adm3')

    for commune_gadm in communes_gadm:
        parent_loc = munis_gadm.get(srcid=commune_gadm.id_2).location
        hcid = u"%s%s" % (parent_loc.hcid, commune_gadm.name[:2].upper())
        if Location.objects.filter(hcid=hcid):
            hcid = u"%s%s-%s" % (
                parent_loc.hcid, commune_gadm.name[:2].upper(),
                commune_gadm.srcid
            )

        commune_loc = Location.objects.create(
            name=smart_text(commune_gadm.name.strip().title()),
            loc_type=commune_type,
            hcid=hcid, srcid=commune_gadm.srcid, parent=parent_loc,
            alt_names=smart_text(commune_gadm.varname.strip()))
        commune_gadm.location = commune_loc
        commune_gadm.save()
        print u"3: %s - %s" % (commune_gadm.location, commune_loc.hcid)

    return True


@python_2_unicode_compatible
def sites_to_loc():
    sites = SiteLocation.objects.all()
    site_type = LocationType.objects.get(code='adm6')

    for site in sites:
        try:
            parent_gadm = Gadm.objects.get(geom__contains=site.geom,
                                           loctype="Commune")
            parent_loc = parent_gadm.location
            hcid = u"%s%s" % (
                parent_loc.hcid, parent_loc.get_descendant_count() + 1
            )

        except Gadm.DoesNotExist:
            parent_loc = Location.objects.get(pk=1)
            hcid = u"%s%s" % (
                parent_loc.hcid, parent_loc.get_descendant_count() + 1
            )

        loc = Location.objects.create(parent=parent_loc,
                                      name=smart_text(site.name.strip()),
                                      alt_names=smart_text(
                                          site.altname.strip()), hcid=hcid,
                                      srcid=site.code, loc_type=site_type,
                                      fac_type=site.factype)

        site.location = loc
        site.save()
        print u"%s - %s" % (loc.parent, loc.name)

    return
