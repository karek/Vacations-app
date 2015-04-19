# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from planner.utils import dateToString
from datetime import date, timedelta
from django.core.mail import send_mail

class Team(models.Model):
    name = models.CharField(max_length=30, blank=False)

    def __unicode__(self):  # __unicode__ on Python 2
        return self.name

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class EmailUserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, team, password=None, is_teamleader=False):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            is_teamleader=is_teamleader,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, team, password, is_teamleader=False):
        user = self.create_user(email,
                                password=password,
                                first_name=first_name,
                                last_name=last_name,
                                is_teamleader=is_teamleader,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class EmailUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_teamleader = models.BooleanField(default=False)
    team = models.ForeignKey(Team, blank=True, null=True)

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def clean(self):
        super(EmailUser, self).clean()
        if self.email is not None:
            self.email = self.email.lower()
            if self._state.adding:
                emailuser = EmailUser.objects.filter(email__iexact=self.email)

                if emailuser.exists():
                    raise ValidationError({
                        'email': 'That email address is already associated with an account.'
                    })

    def get_full_name(self):
        # The user is identified by their email address
        return unicode(self.first_name) + " " + unicode(self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __unicode__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def toDict(self):
        if self.team:
            team_name = self.team.name
        else:
            team_name = ''

        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'team' : team_name,
            'is_teamleader' : self.is_teamleader,
        }

    def is_manager_of(self, other):
        """ Is this user manager of someone's team? """
        # TODO: is a team leader his own manager?
        return self.team == other.team and self.is_teamleader

class AbsenceKind(models.Model):
    name = models.CharField(max_length=30, blank=False, unique=True)
    require_acceptance = models.BooleanField(default=True)

    def __unicode__(self):  # __unicode__ on Python 2
        return self.name

class Absence(models.Model):
    """ User's whole Absence. Describes parameters and has many AbsenceRanges attached. """
    
    #Status choices
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )

    user = models.ForeignKey(EmailUser)
    dateCreated = models.DateTimeField(auto_now_add=True)
    # Only for debug purpouse
    # Change it when front allows
    absence_kind = models.ForeignKey(AbsenceKind, null=True, blank=True)
    status = models.IntegerField(default=PENDING, choices=STATUS_CHOICES)
    # TODO: komentarz

    def __unicode__(self):
        return "Absence by %s" % (self.id, self.user)

    @classmethod
    @transaction.atomic
    def createFromRanges(cls, user, ranges):
        """ Create an absence together with all its absence ranges (in one atomic transaction)."""
        new_abs = cls(user=user)
        new_abs.save()
        for (rbegin, rend) in ranges:
            new_range = AbsenceRange(absence=new_abs, begin=rbegin, end=rend)
            new_range.full_clean()
            new_range.save()
        # if the absence doesn't need acceptance, skip to ACCEPTED
        if new_abs.absence_kind and new_abs.absence_kind.reqiure_acceptance:
            new_abs.accept()
        else:
            #send mail to our test email to check if its ok
            # TODO send a proper mail to the right address
            send_mail(new_abs.mail_request_title(), new_abs.mail_request_body(),
                    'tytusdjango@gmail.com', ['tytusdjango@gmail.com'])
        return new_abs

    def toDict(self):
        """ Returns needed Absence's attributes as dict, e.g. for converting to json. """
        return {
            'id': self.id,
            'user_id': self.user.id,
            'user_name': self.user.get_full_name(),
            'date_created': dateToString(self.dateCreated),
            # TODO delete the ifs below when we have obligatory kind selection
            'kind': self.absence_kind.id if self.absence_kind else -1,
            'kind_name': self.absence_kind.name if self.absence_kind else 'none',
        }

    def accept(self):
        self.status = self.ACCEPTED
        # TODO send a proper mail to the right address
        # TODO in the current form the email could be send BOTH to user and HR
        send_mail(self.mail_accepted_title(), self.mail_accepted_body(),
                'tytusdjango@gmail.com', ['tytusdjango@gmail.com'])
        self.save()

    def reject(self):
        # TODO co dalej sie dzieje z takim urlopem? przeciez nie ma po co wisiec w bazie na zawsze
        self.status = self.REJECTED
        # TODO send a proper mail to the right address
        send_mail(self.mail_rejected_title(), self.mail_rejected_body(),
                'tytusdjango@gmail.com', ['tytusdjango@gmail.com'])
        self.save()

    def description(self):
        body = ('Absence by: ' + self.user.get_full_name() + '\n'
                'Requested on: ' + dateToString(self.dateCreated) + '\n'
                'Absence kind: ' + (self.absence_kind.name if self.absence_kind else 'none') + '\n'
                'For days:\n')
        for r in AbsenceRange.objects.filter(absence=self).order_by('begin', 'end'):
            body += ' * ' + unicode(r) + '\n'
        return body
    
    def mail_request_title(self):
        return 'Absence request from ' + self.user.get_full_name()

    def mail_request_body(self):
        desc = self.description()
        mng_url = settings.BASE_URL + '/manage-absence'
        return desc + ('\n' +
                'to accept: ' + mng_url + '?accept-submit&absence-id=' + str(self.id) + '\n'
                'to reject: ' + mng_url + '?reject-submit&absence-id=' + str(self.id) + '\n'
                'to view details: ' + mng_url + '?absence-id=' + str(self.id) + '\n')

    def mail_accepted_title(self):
        return 'Absence was accepted'

    def mail_accepted_body(self):
        return ('Absence request (listed below) was accepted. Have fun!\n\n' +
                self.description())

    def mail_rejected_title(self):
        return 'Absence was REJECTED'

    def mail_rejected_body(self):
        return ('Absence request (listed below) was REJECTED. Try harder next time!\n\n' + 
                self.description())


class AbsenceRange(models.Model):
    """ A single, continous period of absence as part of an Absence. """
    absence = models.ForeignKey(Absence)
    begin = models.DateField()
    end = models.DateField()

    def __unicode__(self):
        return "%s - %s" % (dateToString(self.begin), dateToString(self.end))

    @classmethod
    def getBetween(cls, users, rbegin, rend):
        """ Returns all users' vacations intersecting with given period.
        
        users should be a list of users or '*' for everyone. """
        # first of all: don't show rejected absences
        user_ranges = cls.objects.exclude(absence__status=Absence.REJECTED)
        # second, filter needed users
        if users != '*':
            user_ranges = user_ranges.filter(absence__user__in=users)
        # finally, filter given dates
        return user_ranges.filter(
            Q(begin__lt=rend, begin__gte=rbegin) | Q(end__gt=rbegin, end__lte=rend),
        ).order_by('begin', 'end')

    @classmethod
    def getIntersection(cls, user, rbegin, rend):
        """ Does the user already have any absence range during given period?
        
        Returns single (first if many) intersecting AbsenceRange or None. """
        try:
            return cls.objects.exclude(absence__status=Absence.REJECTED).filter(
                Q(begin__lt=rend, begin__gte=rbegin) | Q(end__gt=rbegin, end__lte=rend),
                absence__user=user)[0]
        except IndexError:
            return None

    def clean(self):
        """ Don't allow adding intersecting ranges. """
        if self.begin >= self.end:
            raise ValidationError("Range begin (%s) is after its end (%s)"
                                  % (dateToString(self.begin), dateToString(self.end)))
        print "clean for range %s" % self
        # TODO: we should allow intersections with absences of other types in the future
        intersecting = self.getIntersection(self.absence.user, self.begin, self.end)
        if intersecting:
            raise ValidationError("new absence %s intersects with %s" % (self, intersecting))

    def toDict(self):
        """ Returns needed AbsenceRange's attributes as dict, e.g. for converting to json. """
        return {
            'id': self.id,
            'begin': dateToString(self.begin),
            'end': dateToString(self.end),
            'absence_id': self.absence.id,
            'user_id': self.absence.user.id,
            'status': self.absence.status,
        }


class Holiday(models.Model):
    """ A single work-free day. """
    day = models.DateField()
    name = models.CharField(max_length=30, blank=False)

    def __unicode__(self):
        return '%s : %s' % (self.day, self.name)

    @classmethod
    def dateRange(cls, start_date, end_date):
        for n in xrange(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @classmethod        
    def yearRange(cls, year):
        return cls.dateRange(date(year, 1, 1), date(year + 1, 1, 1))

    @classmethod    
    def weekends(cls, year):
        return ((weekend, weekend.strftime("%A")) for weekend in cls.yearRange(year) 
            if weekend.weekday() == 5 or weekend.weekday() == 6)

    # TODO: FK to HolidayCalendar

    def toDict(self):
        return {
            'id': self.id,
            'day': dateToString(self.day),
            'name': self.name,
        }


