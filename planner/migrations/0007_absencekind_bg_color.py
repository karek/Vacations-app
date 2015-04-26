# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0006_manual_count_workdays'),
    ]

    operations = [
        migrations.AddField(
            model_name='absencekind',
            name='bg_color',
            field=colorful.fields.RGBColorField(default=b'#888888'),
            preserve_default=True,
        ),
    ]
