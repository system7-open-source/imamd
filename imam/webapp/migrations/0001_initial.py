# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PdfForms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('formName', models.CharField(max_length=128, verbose_name='Form Name')),
                ('slug', models.SlugField(unique=True)),
                ('pdfFile', models.FileField(upload_to='pdf_forms', verbose_name='Pdf File')),
            ],
            options={
                'verbose_name': 'Pdf Form',
                'verbose_name_plural': 'Pdf Forms',
            },
            bases=(models.Model,),
        ),
    ]
