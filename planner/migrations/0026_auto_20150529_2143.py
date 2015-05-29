# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0025_auto_20150529_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holidaycalendar',
            name='selectedByDefault',
            field=models.BooleanField(default=False, verbose_name=b'selected by default in registration form'),
            preserve_default=True,
        ),
    ]
