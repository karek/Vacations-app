# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0016_absence_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='comment',
            field=models.CharField(default=b'', max_length=81),
            preserve_default=True,
        ),
    ]
