# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0003_auto_20150419_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailuser',
            name='team',
            field=models.ForeignKey(default=1, to='planner.Team'),
            preserve_default=False,
        ),
    ]
