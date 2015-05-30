# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0026_auto_20150529_2143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='holidaycalendar',
            old_name='selectedByDefault',
            new_name='selected_by_default',
        ),
    ]
