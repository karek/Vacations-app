# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0018_auto_20150428_0339'),
    ]

    operations = [
        migrations.AddField(
            model_name='absence',
            name='dateModified',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 17, 8, 42, 41, 991624, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='absence',
            name='dateCreated',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
