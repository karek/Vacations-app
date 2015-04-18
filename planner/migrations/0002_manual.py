# -*- coding: utf-8 -*-
from django.db import models, migrations

def create_teams(apps, schema_editor):
	Team = apps.get_model("planner", "Team")

	t1 = Team(name="Drużyna 1")
	t1.save()
	t2 = Team(name="Kosmici")
	t2.save()
	t3 = Team(name="Dowództwo")
	t3.save()

def create_users(apps, schema_editor):
    Team = apps.get_model("planner", "Team")
    User = apps.get_model("planner", "EmailUser")
    
    t1 = Team.objects.get(name="Drużyna 1")
    t2 = Team.objects.get(name="Kosmici")
    t3 = Team.objects.get(name="Dowództwo")
    
    admin = User(email='admin@admin.pl', first_name='admin', last_name='admin', team=t3, password='admin', is_teamleader=True)
    admin.is_admin = True
    users = [
    	admin,
    	User(email='tytus.bomba@gwiezdaflota.pl',first_name='Tytus',last_name='Bomba',team=t1, is_teamleader=True),
    	User(email='kapitan.glus@gwiezdaflota.pl',first_name='Kapitan',last_name='Głuś',team=t1),
    	User(email='sultan.kosmitow@kosmici.pl',first_name='Sułtan',last_name='Kosmitów',team=t2, is_teamleader=True),
    	User(email='michal.parchas@kosmici.pl',first_name='Michał',last_name='Parchaś',team=t2),
    	User(email='admirał.torpeda@gwiezdaflota.pl',first_name='Admirał',last_name='Torpeda',team=t3)
    	]
    User.objects.bulk_create(users)

class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_teams),
        migrations.RunPython(create_users),
    ]