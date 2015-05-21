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
    HolidayCalendar = apps.get_model("planner", "HolidayCalendar")

    days = weekends(2015)
    holidays = [Holiday(day=day, name=name) for (day, name) in days]

    weekend_calendar = HolidayCalendar(name='Weekends for 2015')
    weekend_calendar.save()

    for weekend in holidays:
        weekend.save()
        weekend_calendar.holidays.add(weekend)


def create_holiday_calendar(apps, schema_editor):
    Holiday = apps.get_model("planner", "Holiday")
    HolidayCalendar = apps.get_model("planner", "HolidayCalendar")

    admiral_bday = Holiday.objects.get(name="Urodziny Admirała")
    rks_game = Holiday.objects.get(name="Mecz RKS HUWDU")
    building_starfleeet = Holiday.objects.get(name="Rocznica ustanowienia Gwiezdnej floty")
    sultan_bday = Holiday.objects.get(name="Urodziny Sułtana Kosmitów")

    fleet_holidays = HolidayCalendar(name="Dni wolne od pracy w Gwiezdnej Flocie")
    fleet_holidays.save()
    fleet_holidays.holidays.add(admiral_bday, rks_game, building_starfleeet)

    aliens_holidays = HolidayCalendar(name="Dni wolne od pracy kosmitów")
    aliens_holidays.save()
    aliens_holidays.holidays.add(sultan_bday, rks_game)


def set_holidays(apps, schema_editor):

    EmailUser = apps.get_model("planner", "EmailUser")
    Team = apps.get_model("planner", "Team")
    HolidayCalendar = apps.get_model("planner", "HolidayCalendar")

    fleet_holidays = HolidayCalendar.objects.get(name="Dni wolne od pracy w Gwiezdnej Flocie")
    aliens_holidays = HolidayCalendar.objects.get(name="Dni wolne od pracy kosmitów")
    weekend_calendar = HolidayCalendar.objects.get(name='Weekends for 2015')

    fleet = EmailUser.objects.all().exclude(team=Team.objects.get(name="Kosmici"))
    aliens = EmailUser.objects.all().filter(team=Team.objects.get(name="Kosmici"))

    for user in fleet:
        user.holidays.add(fleet_holidays, weekend_calendar)
        user.save()

    for user in aliens:
        user.holidays.add(aliens_holidays, weekend_calendar)
        user.save()


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0021_auto_20150521_1147'),
    ]

    operations = [
        migrations.RunPython(add_weekends),
        migrations.RunPython(create_holiday_calendar),
        migrations.RunPython(set_holidays)
    ]
