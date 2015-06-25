# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0028_auto_20150530_0943'),
    ]

    operations = [
        migrations.RenameField(
            model_name='absence',
            old_name='dateModified',
            new_name='date_modified',
        ),
    ]
