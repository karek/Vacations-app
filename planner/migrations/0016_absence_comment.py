# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_comment(apps, schema_editor):
    Absence = apps.get_model("planner", "Absence")
    User = apps.get_model("planner", "EmailUser")

    u = User.objects.get(email='tytus.bomba@gwiezdaflota.pl')

    # STATUS 1 = ACCEPTED
    a = Absence.objects.get(id=1)
    a.comment = "Wyjazd z Andżelą do Władysławowa"
    a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0015_auto_20150427_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='absence',
            name='comment',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.RunPython(add_comment),
    ]
