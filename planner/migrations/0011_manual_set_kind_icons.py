# -*- coding: utf-8 -*-
from datetime import date

from django.db import models, migrations


def set_absencekind_icons(apps, schema_editor):
    AbsenceKind = apps.get_model("planner", "AbsenceKind")
    icons = {
        'Vacations': 'plane',
        'On request': 'exclamation-sign',
        'Sickness': 'plus',
        'Homeworking': 'home',
        'Delegation': 'briefcase',
        'Parental': 'user',
    }
    for kindname, icon in icons.items():
        kind = AbsenceKind.objects.get(name=kindname)
        kind.icon_name = icon
        kind.save()


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0010_absencekind_icon_name'),
    ]

    operations = [
            migrations.RunPython(set_absencekind_icons)
    ]
