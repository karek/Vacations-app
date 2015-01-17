from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from planner.utils import dateToString


class EmailUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email,
                                password=password,
                                first_name=first_name,
                                last_name=last_name
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

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def get_full_name(self):
        # The user is identified by their email address
        return str(self.first_name) + " " + str(self.last_name)

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


class Absence(models.Model):
    """ User's whole Absence. Describes parameters and has many AbsenceRanges attached. """
    user = models.ForeignKey(EmailUser)
    dateCreated = models.DateTimeField(auto_now_add=True)
    # TODO: rodzaj
    # TODO: status
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
            absence = AbsenceRange(absence=new_abs, begin=rbegin, end=rend)
            absence.full_clean()
            absence.save()
        return new_abs


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
        user_ranges = cls.objects.all()
        # TODO: this should return whole Absences, not single ranges.
        if users != '*':
            user_ranges = user_ranges.filter(absence__user__in=users)
        return user_ranges.filter(
                Q(begin__lt=rend, begin__gte=rbegin) | Q(end__gt=rbegin, end__lte=rend),
                ).order_by('begin', 'end')

    @classmethod
    def getIntersection(cls, user, rbegin, rend):
        """ Does the user already have any absence range during given period?
        
        Returns single (first if many) intersecting AbsenceRange or None. """
        try:
            return cls.objects.filter(
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


