# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0009_manual_set_colors'),
    ]

    operations = [
        migrations.AddField(
            model_name='absencekind',
            name='icon_name',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
