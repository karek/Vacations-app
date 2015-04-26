# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime

from django.db import models, migrations


# copied from model because migration don't allow usage of model's methods
def dateRange(start_date, end_date):
    for n in xrange(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def yearRange(year):
    return dateRange(date(year, 1, 1), date(year + 1, 1, 1))

def weekends(year):
    return ((weekend, weekend.strftime("%A")) for weekend in yearRange(year)
            if weekend.weekday() == 5 or weekend.weekday() == 6)


def add_weekends(apps, schema_editor):
    Holiday = apps.get_model("planner", "Holiday")

    days = weekends(2015)
    holidays = [Holiday(day=day, name=name) for (day,name) in days]

    Holiday.objects.bulk_create(holidays)


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0012_auto_20150426_1835'),
    ]

    operations = [
            migrations.RunPython(add_weekends)
    ]
