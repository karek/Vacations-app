# -*- coding: utf-8 -*-
from datetime import date

from django.db import models, migrations


def set_absencekind_colors(apps, schema_editor):
    AbsenceKind = apps.get_model("planner", "AbsenceKind")
    colors = {
        'Vacations': '#339933',
        'On request': '#dba429',
        'Sickness': '#d44384',
        'Homeworking': '#417ddb',
        'Delegation': '#7738e8',
        'Parental': '#db3027',
    }
    for kindname, color in colors.items():
        kind = AbsenceKind.objects.get(name=kindname)
        kind.text_color = '#ffffff'
        kind.bg_color = color
        kind.save()


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0008_auto_20150426_1651'),
    ]

    operations = [
            migrations.RunPython(set_absencekind_colors)
    ]
