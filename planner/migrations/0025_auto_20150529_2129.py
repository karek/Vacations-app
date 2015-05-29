# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_default_for_weekends(apps, schema_editor):
    HolidayCalendar = apps.get_model('planner', 'HolidayCalendar')
    for cal in HolidayCalendar.objects.filter(name='Weekends'):
        cal.selectedByDefault = True
        cal.save()
    for cal in HolidayCalendar.objects.filter(name='Dni wolne od pracy w Gwiezdnej Flocie'):
        cal.selectedByDefault = True
        cal.save()

class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0024_auto_20150521_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='emailuser',
            options={'verbose_name': 'employee', 'verbose_name_plural': 'employees'},
        ),
        migrations.AddField(
            model_name='holidaycalendar',
            name='selectedByDefault',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(set_default_for_weekends),
    ]
