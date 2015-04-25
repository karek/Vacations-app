# -*- coding: utf-8 -*-
from datetime import date

from django.db import models, migrations


# copied from model because migration don't allow usage of model's methods
def workday_count(abs_range, apps):
    Holiday = apps.get_model("planner", "Holiday")
    holidays = (Holiday.objects.filter(day__gte=abs_range.begin, day__lt=abs_range.end)
            .values('day').distinct())
    return (abs_range.end - abs_range.begin).days - holidays.count()


def count_total_workdays(apps, schema_editor):
    Absence = apps.get_model("planner", "Absence")
    AbsenceRange = apps.get_model("planner", "AbsenceRange")
    for absence in Absence.objects.all():
        absence.total_workdays = 0
        for abs_range in AbsenceRange.objects.filter(absence=absence):
            absence.total_workdays += workday_count(abs_range, apps)
        absence.save()


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0005_absence_total_workdays'),
    ]

    operations = [
            migrations.RunPython(count_total_workdays)
    ]
