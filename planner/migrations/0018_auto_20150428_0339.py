# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0017_auto_20150428_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='dateCreated',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
    ]
