# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0007_absencekind_bg_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='absencekind',
            name='text_color',
            field=colorful.fields.RGBColorField(default=b'#ffffff', verbose_name=b'Event text color'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='absencekind',
            name='bg_color',
            field=colorful.fields.RGBColorField(default=b'#888888', verbose_name=b'Event background color'),
            preserve_default=True,
        ),
    ]
