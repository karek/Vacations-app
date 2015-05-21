# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0022_manual_holiday_calendar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='absence',
            name='dateModified',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='holiday',
            name='calendar',
            field=models.ForeignKey(to='planner.HolidayCalendar'),
            preserve_default=True,
        ),
    ]
