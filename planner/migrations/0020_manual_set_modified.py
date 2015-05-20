# -*- coding: utf-8 -*-
from datetime import date

from django.db import models, migrations


def set_modified_to_created(apps, schema_editor):
    Absence = apps.get_model("planner", "Absence")
    # manuallt setting an "auto_now" field is a bit hacky
    for absence in Absence.objects.all():
        for field in absence._meta.local_fields:
            if field.name == "dateModified":
                field.auto_now = False
        absence.dateModified = absence.dateCreated
        absence.save()
        for field in absence._meta.local_fields:
            if field.name == "dateModified":
                field.auto_now = True


class Migration(migrations.Migration):
    dependencies = [
        ('planner', '0019_auto_20150517_1042'),
    ]

    operations = [
            migrations.RunPython(set_modified_to_created)
    ]
