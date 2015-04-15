# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0003_emailuser_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailuser',
            name='is_teamleader',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
