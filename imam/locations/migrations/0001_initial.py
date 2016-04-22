# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import django.contrib.gis.db.models.fields
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gadm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cc', models.CharField(max_length=15, null=True, blank=True)),
                ('engtype', models.CharField(max_length=50, null=True, blank=True)),
                ('loctype', models.CharField(max_length=50, null=True, blank=True)),
                ('hasc', models.CharField(max_length=15, null=True, blank=True)),
                ('id_0', models.IntegerField(null=True, blank=True)),
                ('id_1', models.IntegerField(null=True, blank=True)),
                ('id_2', models.IntegerField(null=True, blank=True)),
                ('id_3', models.IntegerField(null=True, blank=True)),
                ('srcid', models.IntegerField(null=True, blank=True)),
                ('iso', models.CharField(max_length=3, null=True, blank=True)),
                ('name', models.CharField(max_length=75, null=True, blank=True)),
                ('name_0', models.CharField(max_length=75, null=True, blank=True)),
                ('name_1', models.CharField(max_length=75, null=True, blank=True)),
                ('name_2', models.CharField(max_length=75, null=True, blank=True)),
                ('name_3', models.CharField(max_length=75, null=True, blank=True)),
                ('nl_name', models.CharField(max_length=50, null=True, blank=True)),
                ('remark', models.CharField(max_length=125, null=True, blank=True)),
                ('shape_area', models.FloatField()),
                ('shape_leng', models.FloatField()),
                ('validfr', models.CharField(max_length=25, null=True, blank=True)),
                ('validto', models.CharField(max_length=25, null=True, blank=True)),
                ('varname', models.CharField(max_length=150, null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'verbose_name': 'GADM Administrative Boundaries',
                'verbose_name_plural': 'GADM Administrative Boundaries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default='Unknown Name', max_length=100)),
                ('alt_names', models.CharField(help_text='List of Alternate Place Names separated by (|)', max_length=150, null=True, blank=True)),
                ('hcid', models.CharField(null=True, max_length=16, blank=True, help_text=b'Unique ID: AABBCC##', unique=True, db_index=True)),
                ('srcid', models.CharField(help_text='Code provided from source agency. HASC for GADM shapes.', max_length=75, null=True, db_index=True, blank=True)),
                ('fac_type', models.CharField(blank=True, max_length=5, null=True, choices=[(b'HP', 'Health Post'), (b'MH', 'Mental Hospital'), (b'MC', 'Maternity Center'), (b'HC', 'Health Center'), (b'CH', 'Central Hospital'), (b'HOS', 'Hospital'), (b'WH', 'Warehouse'), (b'OTHER', 'Other')])),
                ('slug', django_extensions.db.fields.AutoSlugField(editable=False, populate_from=b'hcid', max_length=16, blank=True, unique=True)),
                ('uuid', django_extensions.db.fields.UUIDField(editable=False, name=b'uuid', blank=True)),
                ('created_at', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('updated_at', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=6)),
                ('name', models.CharField(max_length=75, null=True, blank=True)),
                ('alt_names', models.CharField(max_length=75, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Location Type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.IntegerField(null=True)),
                ('factype', models.CharField(max_length=80, null=True, blank=True)),
                ('name', models.CharField(max_length=80, null=True, blank=True)),
                ('altname', models.CharField(max_length=80, null=True, blank=True)),
                ('adm1_name', models.CharField(max_length=80, null=True, blank=True)),
                ('adm1_code', models.IntegerField(null=True)),
                ('adm2_name', models.CharField(max_length=80, null=True, blank=True)),
                ('adm2_code', models.IntegerField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('zonetype', models.CharField(max_length=80, null=True, blank=True)),
                ('nutrition', models.CharField(max_length=80, null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location', models.OneToOneField(related_name=b'location_pnt', null=True, blank=True, to='locations.Location')),
            ],
            options={
                'verbose_name': 'Health Site',
                'verbose_name_plural': 'Health Sites',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='location',
            name='loc_type',
            field=models.ForeignKey(to='locations.LocationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name=b'children', to='locations.Location', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gadm',
            name='location',
            field=models.OneToOneField(related_name=b'location_gadm', null=True, blank=True, to='locations.Location'),
            preserve_default=True,
        ),
    ]
