# -*- coding: utf-8 -*-
from django.db import models, migrations
from datetime import date

def create_teams(apps, schema_editor):
	Team = apps.get_model("planner", "Team")

	t1 = Team(name="Drużyna 1")
	t2 = Team(name="Kosmici")
	t3 = Team(name="Dowództwo")

	Team.objects.bulk_create([t1,t2,t3])

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
    	User(email='chorazy.glus@gwiezdaflota.pl',first_name='Chorąży',last_name='Głuś',team=t1),
    	User(email='sultan.kosmitow@kosmici.ru',first_name='Sułtan',last_name='Kosmitów',team=t2, is_teamleader=True),
    	User(email='michal.parchas@kosmici.ru',first_name='Michał',last_name='Parchaś',team=t2),
    	User(email='admirał.torpeda@gwiezdaflota.pl',first_name='Admirał',last_name='Torpeda',team=t3)
    	]
    User.objects.bulk_create(users)

def create_holidays(apps, schema_editor):
	Holiday = apps.get_model("planner", "Holiday")

	holidays = [
		Holiday(day=date(2015,4,29), name="Urodziny Admirała"),
		Holiday(day=date(2015,4,24), name="Mecz RKS HUWDU"),
		Holiday(day=date(2015,5,1), name="Rocznica ustanowienia Gwiezdnej floty"),
		Holiday(day=date(2015,4,21), name="Urodziny Sułtana Kosmitów")
	]
	Holiday.objects.bulk_create(holidays)

def create_absences(apps, schema_editor):
	Absence = apps.get_model("planner", "Absence")
	AbsenceRange = apps.get_model("planner", "AbsenceRange")
	User = apps.get_model("planner", "EmailUser")

	u1 = User.objects.get(email='tytus.bomba@gwiezdaflota.pl')
	u2 = User.objects.get(email='chorazy.glus@gwiezdaflota.pl')  
	u3 = User.objects.get(email='sultan.kosmitow@kosmici.ru')

	a1 = Absence(user = u1, dateCreated=date(2015,4,16))
	a1.save()
	a2 = Absence(user = u1, dateCreated=date(2015,4,14))
	a2.save()
	a3 = Absence(user = u2, dateCreated=date(2015,4,15))
	a3.save()
	a4 = Absence(user = u3, dateCreated=date(2015,4,18))
	a4.save()

	absences_ranges = [
		AbsenceRange(
			absence=a1, 
			begin=date(2015,4,27), 
			end=date(2015,5,3)),
		AbsenceRange(
			absence=a1, 
			begin=date(2015,4,21), 
			end=date(2015,4,22)),
		AbsenceRange(
			absence=a2, 
			begin=date(2015,4,23), 
			end=date(2015,4,24)),
        AbsenceRange(
			absence=a3, 
			begin=date(2015,4,28), 
			end=date(2015,4,30)),
		AbsenceRange(
			absence=a4, 
			begin=date(2015,4,19), 
			end=date(2015,4,23)),
		]
	AbsenceRange.objects.bulk_create(absences_ranges)

class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_teams),
        migrations.RunPython(create_users),
        migrations.RunPython(create_holidays),
        migrations.RunPython(create_absences),
    ]
