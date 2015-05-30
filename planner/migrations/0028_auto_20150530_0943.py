# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0027_auto_20150530_0935'),
    ]

    operations = [
        migrations.RenameField(
            model_name='absence',
            old_name='dateCreated',
            new_name='date_created',
        ),
    ]
