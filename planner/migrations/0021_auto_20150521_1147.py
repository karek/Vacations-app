# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0020_manual_set_modified'),
    ]

    operations = [
        migrations.CreateModel(
            name='HolidayCalendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('holidays', models.ManyToManyField(to='planner.Holiday')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='emailuser',
            name='holidays',
            field=models.ManyToManyField(to='planner.HolidayCalendar'),
            preserve_default=True,
        ),
    ]
