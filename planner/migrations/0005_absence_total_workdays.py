# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0004_auto_20150425_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='absence',
            name='total_workdays',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
