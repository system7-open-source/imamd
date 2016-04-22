# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rapidsms', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=8, db_index=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InventoryLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_quantity_received', models.IntegerField()),
                ('current_holding', models.IntegerField()),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('alt_description', models.CharField(max_length=255, null=True, blank=True)),
                ('code', models.CharField(unique=True, max_length=8, db_index=True)),
                ('alt_code', models.CharField(max_length=8, unique=True, null=True, blank=True)),
                ('unit', models.CharField(max_length=16)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationProgramState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('training_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('last_report_date', models.DateTimeField(default=None, null=True, blank=True)),
                ('current_state', models.CharField(default='OUT', max_length=20, choices=[('OUT', 'Not part of program'), ('INACTIVE-TRAINED', 'Trained (but without data)'), ('ACTIVE-BAD', 'Active with bad data'), ('ACTIVE', 'Active with (some) good data'), ('INACTIVE-NEW', 'Recently inactive (8-16 weeks ago)'), ('INACTIVE', 'Inactive')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LowStockAlert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('item', models.ForeignKey(to='core.Item')),
                ('site', models.ForeignKey(to='locations.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PatientGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('code', models.CharField(unique=True, max_length=8, db_index=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('email', models.EmailField(max_length=75, null=True, verbose_name='Email', blank=True)),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('contact', models.OneToOneField(related_name='worker', to='rapidsms.Contact')),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('alt_description', models.CharField(max_length=100, null=True, blank=True)),
                ('code', models.CharField(unique=True, max_length=8, db_index=True)),
                ('alt_code', models.CharField(max_length=8, unique=True, null=True, blank=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('loc_type', models.ForeignKey(related_name='+', blank=True, to='locations.LocationType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('code', models.CharField(unique=True, max_length=8, db_index=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('acronym', models.CharField(unique=True, max_length=8, db_index=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('period_number', models.PositiveIntegerField(verbose_name='Report period')),
                ('report_date', models.DateField(verbose_name='period date')),
                ('patients_at_period_start', models.IntegerField(null=True)),
                ('new_marasmic_patients', models.IntegerField(null=True, verbose_name='New admissions')),
                ('new_oedema_patients', models.IntegerField(null=True)),
                ('new_relapsed_patients', models.IntegerField(null=True)),
                ('hiv_positive_patients', models.IntegerField(null=True)),
                ('readmitted_patients', models.IntegerField(null=True)),
                ('patients_transferred_in', models.IntegerField(null=True, verbose_name='Transfers (IN)')),
                ('patients_transferred_out', models.IntegerField(null=True, verbose_name='Transfers (OUT)')),
                ('patient_deaths', models.IntegerField(null=True, verbose_name='Deaths')),
                ('confirmed_patient_defaults', models.IntegerField(null=True)),
                ('unconfirmed_patient_defaults', models.IntegerField(null=True, verbose_name='Defaults')),
                ('unresponsive_patients', models.IntegerField(null=True, verbose_name='No response')),
                ('patients_cured', models.IntegerField(null=True, verbose_name='Cured')),
                ('patients_at_period_end', models.IntegerField(null=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('group', models.ForeignKey(verbose_name='Group', to='core.PatientGroup')),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('program', models.ForeignKey(to='core.Program')),
                ('reporter', models.ForeignKey(to='core.Personnel', null=True)),
                ('site', models.ForeignKey(verbose_name='Location', to='locations.Location')),
            ],
            options={
                'ordering': ('-report_date', '-created', '-pk'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockOutReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('items', models.ManyToManyField(to='core.Item')),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('reporter', models.ForeignKey(to='core.Personnel', null=True)),
                ('site', models.ForeignKey(verbose_name='Location', to='locations.Location')),
            ],
            options={
                'ordering': ('-created', '-pk'),
                'abstract': False,
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StockReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('logs', models.ManyToManyField(to='core.InventoryLog')),
                ('reporter', models.ForeignKey(to='core.Personnel', null=True)),
                ('site', models.ForeignKey(verbose_name='Location', to='locations.Location')),
            ],
            options={
                'ordering': ('-created', '-pk'),
                'abstract': False,
                'get_latest_by': 'created',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='program',
            name='category',
            field=models.ForeignKey(related_name='programs', to='core.ProgramCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='program',
            name='created_by',
            field=models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='program',
            name='last_modified_by',
            field=models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='program',
            name='sites',
            field=models.ManyToManyField(related_name='site_programs', to='locations.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personnel',
            name='position',
            field=models.ForeignKey(related_name='+', verbose_name='Position', to='core.Position'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personnel',
            name='site',
            field=models.ForeignKey(related_name='workers', verbose_name='Location', to='locations.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personnel',
            name='user',
            field=models.OneToOneField(related_name='worker', null=True, blank=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationprogramstate',
            name='program',
            field=models.ForeignKey(to='core.Program'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='locationprogramstate',
            name='site',
            field=models.OneToOneField(to='locations.Location'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='locationprogramstate',
            unique_together=set([('site', 'program')]),
        ),
        migrations.AddField(
            model_name='inventorylog',
            name='item',
            field=models.ForeignKey(to='core.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventorylog',
            name='last_modified_by',
            field=models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
