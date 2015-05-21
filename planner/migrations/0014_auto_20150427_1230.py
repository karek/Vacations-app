# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0012_auto_20150426_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='status',
            field=models.IntegerField(
                default=0, choices=[(0, b'Pending'), (1, b'Accepted'), (2, b'Rejected'), (3, b'Cancelled')]),
            preserve_default=True,
        ),
    ]
