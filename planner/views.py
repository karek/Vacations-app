from calendar import monthrange
from datetime import date

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic.edit import FormView
from planner.forms import RegisterForm, YearForm
from planner.models import Absence, AbsenceRange
from planner.utils import InternalError, stringToDate, dateToString, objListToJson

class IndexView(View):
    def get(self, request, *args, **kwargs):
        d = date.today()
        month_begin = date(d.year, d.month, 1)
        month_end = date(d.year, d.month, monthrange(d.year, d.month)[1])
        context = {
            'month_begin': dateToString(month_begin),
            'month_end': dateToString(month_end),
            'users': objListToJson(get_user_model().objects.all()),
        }
        return render(request, 'planner/index.html', context)


class RegisterView(SuccessMessageMixin, FormView):
    form_class = RegisterForm
    template_name = 'planner/register.html'
    success_url = '/'
    success_message = "Account has been created successfully."

    def get_initial(self):
        initial = super(RegisterView, self).get_initial()
        initial['email'] = self.request.GET.get('email','')
        return initial

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)


def user_login(request):
    next_page = request.GET.get('next', '/')
    if request.method == 'POST':
        email = request.POST['email']
        user = authenticate(email=email)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, 'Logged in succesfully. How are you, %s?' % user.first_name)
            else:
                messages.error(request, 'Your account is disabled.')
                return render(request, 'planner/login.html', {})
        else:
            messages.error(request, 'Invalid login details.')
    return HttpResponseRedirect(next_page)


class PlanAbsenceView(View):
    def get(self, request, *args, **kwargs):
        """ Redirect to index, just in case. """
        return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated():
                raise InternalError("You must log in to plan absences.")
            ranges = self.validateRanges(request.POST.getlist('begin[]'),
                                         request.POST.getlist('end[]'))
            self.addVacation(request.user, ranges)
            messages.success(request, 'Absence booked successfully.')
        except InternalError as e:
            messages.error(request, e.message)
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
            print "added error %s" % e.message
        return HttpResponseRedirect('/')

    def validateRanges(self, begins, ends):
        """ Parse and validate date ranges received from user.

        Takes two lists of 'YYYY-MM-DD' strings.
        Returns validated list of date pairs.
        Throws InternalError on errors.
        """
        if not begins or not ends:
            raise InternalError("no absence ranges given")
        if len(begins) != len(ends):
            raise InternalError("begin[] and end[] sizes differ")
        # Return the ranges, AbsenceRange's clean() will validate the rest
        return sorted(zip(map(stringToDate, begins), map(stringToDate, ends)))

    def addVacation(self, user, ranges):
        """ Takes a list of ranges (date pairs) and saves them as a vacation.
        
        AbsenceRange's clean() checks if the ranges are valid and not intersecting (with themselves
        nor with previous user's absences). """
        Absence.createFromRanges(user, ranges)
        # nothing really to do here


def _make_json_response(data):
    return HttpResponse(data, content_type='application/json')


def _make_error_response(msg):
    return HttpResponseBadRequest(msg, content_type='text/plain')


class UserRestView(View):
    def get(self, request):
        """ Returns all users as array of json objects. """
        return _make_json_response(objListToJson(get_user_model().objects.all()))


class RangeRestView(View):
    def get(self, request):
        """ Returns all ranges between given dates for given users (or everyone if not specified),
        as array of json objects.
        Example call: <server>/get-ranges-between/?begin=2015-01-01&end=2015-01-10&user[]=1&user[]=2
        """
        if 'begin' not in request.GET:
            return _make_error_response('begin not specified')
        if 'end' not in request.GET:
            return _make_error_response('end not specified')
        try:
            rbegin = stringToDate(request.GET['begin'])
            rend = stringToDate(request.GET['end'])
        except InternalError as e:
            return _make_error_response(e.message)
        users = request.GET.getlist('user[]', '*')
        return _make_json_response(objListToJson(AbsenceRange.getBetween(users, rbegin, rend)))

class YearFormView(FormView):

        template_name = 'planner/year_form.html'
        form_class = YearForm
        success_url = '/admin'

            # if 'year' not in request.POST:
            #     return _make_error_response('year not specified')
            # days = Holiday.weekends(request.POST['year'])
            # holidays = [Holiday(day=day, name=name) for (day,name) in days]
            # bulk_create(holidays)
            # return HttpResponseRedirect('/admin')
