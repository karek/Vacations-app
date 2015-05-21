# -*- coding: utf-8 -*-
from datetime import date

from django.db import models, migrations


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

    fleet = EmailUser.objects.all().exclude(team=Team.objects.get(name="Kosmici"))
    aliens = EmailUser.objects.all().filter(team=Team.objects.get(name="Kosmici"))

    for user in fleet:
        user.holidays = fleet_holidays
        user.save()

    for user in aliens:
        user.holidays = aliens_holidays
        user.save()


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0021_auto_20150521_1044'),
    ]

    operations = [
        migrations.RunPython(create_holiday_calendar),
        migrations.RunPython(set_holidays)
    ]
