# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0024_auto_20150521_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailuser',
            options={'verbose_name': 'employee', 'verbose_name_plural': 'employees'},
        ),
        migrations.AlterField(
            model_name='absence',
            name='user',
            field=models.ForeignKey(verbose_name=b'employee', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
