# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0011_manual_set_kind_icons'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absencekind',
            name='icon_name',
            field=models.CharField(help_text=b'See glyphicon-NAME here: http://getbootstrap.com/components/#glyphicons', max_length=20, null=True, verbose_name=b'Glyphicon name', blank=True),
            preserve_default=True,
        ),
    ]
