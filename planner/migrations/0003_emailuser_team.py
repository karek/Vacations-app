# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_holiday_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailuser',
            name='team',
            field=models.ForeignKey(blank=True, to='planner.Team', null=True),
            preserve_default=True,
        ),
    ]
