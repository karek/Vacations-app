# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_manual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='absence_kind',
            field=models.ForeignKey(blank=True, to='planner.AbsenceKind', null=True),
            preserve_default=True,
        ),
    ]
