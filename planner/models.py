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


class Vacation(models.Model):
    """ User's whole vacation. Describes parameters and has many AbsenceRanges attached. """
    # TODO:FIXME: remove blank and null attributes when when logging in works
    user = models.ForeignKey(EmailUser, blank=True, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True)
    # TODO: rodzaj
    # TODO: status
    # TODO: komentarz

    def __unicode__(self):
        return "Vacation by %s" % (self.id, self.user)

    @classmethod
    @transaction.atomic
    def createFromRanges(cls, user, ranges):
        """ Create a vacation together with all its absence ranges (in one atomic transaction)."""
        vac = cls(user=user)
        vac.save()
        for (rbegin, rend) in ranges:
            absence = AbsenceRange(vacation=vac, begin=rbegin, end=rend)
            absence.save()
        return vac


class AbsenceRange(models.Model):
    """ A single, continous period of absence as part of a Vacation. """
    vacation = models.ForeignKey(Vacation)
    begin = models.DateField()
    end = models.DateField()
    # TODO: check if new vacation overlaps with any existing (with the same user)

    def __unicode__(self):
        return "%s - %s" % (dateToString(self.begin), dateToString(self.end))

    @classmethod
    def getBetween(cls, user, rbegin, rend):
        """ Returns all user's vacations intersecting with given period. """
        return cls.objects.filter(
                Q(begin__lt=rend, begin__gte=rbegin) | Q(end__gt=rbegin, end__lte=rend),
                vacation__user=user).order_by('begin', 'end')
