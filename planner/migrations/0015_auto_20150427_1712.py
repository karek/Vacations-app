# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0014_auto_20150427_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='absence_kind',
            field=models.ForeignKey(to='planner.AbsenceKind'),
            preserve_default=True,
        ),
    ]
