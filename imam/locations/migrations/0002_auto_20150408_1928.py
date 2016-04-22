# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name=b'children', blank=True, to='locations.Location', null=True),
        ),
        migrations.AlterField(
            model_name='locationtype',
            name='code',
            field=models.CharField(unique=True, max_length=6),
        ),
    ]
