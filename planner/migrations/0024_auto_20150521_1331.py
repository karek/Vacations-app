# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0023_auto_20150521_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='dateModified',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
