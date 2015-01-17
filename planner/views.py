from calendar import monthrange
from datetime import date

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.base import View
from django.views.generic.edit import FormView

from planner.forms import RegisterForm
from planner.models import Vacation, AbsenceRange
from planner.utils import InternalError, stringToDate, dateToString


class IndexView(View):
    def get(self, request, *args, **kwargs):
        d = date.today()
        month_begin = date(d.year, d.month, 1)
        month_end = date(d.year, d.month, monthrange(d.year, d.month)[1])
        vacations = AbsenceRange.getBetween('*', month_begin, month_end)
        context = { 'booked': vacations }
        return render(request, 'planner/index.html', context)


class RegisterView(SuccessMessageMixin, FormView):
    form_class = RegisterForm
    template_name = 'planner/register.html'
    success_url = '/'
    success_message = "Account has been created successfully."

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = authenticate(email=email)
        if user:
            if user.is_active:
                login(request, user)
                # FIXME this should be done with the 'next' parameter in the url
                return HttpResponseRedirect('/')
            else:
                messages.error(request, 'Your account is disabled.')
                return render(request, 'planner/login.html', {})
        else:
            messages.error(request, 'Invalid login details.')
            return render(request, 'planner/login.html', {})
    else:
        return render(request, 'planner/login.html', {})


class BookVacationView(View):

    def get(self, request, *args, **kwargs):
        """ Redirect to index, just in case. """
        return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        try:
            ranges = self.validateRanges(request.POST.getlist('begin[]'),
                    request.POST.getlist('end[]'))
            self.addVacation(ranges)
            messages.success(request, 'Absence booked successfully.')
        except InternalError as e:
            messages.error(request, e.message)
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
            print "added error %s" % e.message
        return HttpResponseRedirect('/')

    def validateRanges(self, begins, ends):
        """ Validate date ranges received from user.

        Takes two lists of 'YYYY-MM-DD' strings.
        Returns validated list of date pairs.
        Throws InternalError or ValidationError on errors.
        """
        if not begins or not ends:
            raise InternalError("no absence ranges given")
        if len(begins) != len(ends):
            raise InternalError("begin[] and end[] sizes differ")
        # Return the ranges, AbsenceRange's clean() will validate the rest
        return sorted(zip(map(stringToDate, begins), map(stringToDate, ends)))

    def addVacation(self, ranges):
        """ Takes a list of ranges (date pairs) and saves them as a vacation. """
        Vacation.createFromRanges(None, ranges)
        # nothing really to do here

