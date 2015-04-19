from calendar import monthrange
from datetime import date

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.views.generic.edit import FormView
from planner.forms import RegisterForm, YearForm
from planner.models import Absence, AbsenceRange, Holiday
from planner.utils import InternalError, stringToDate, dateToString, objToJson, objListToJson
from datetime import datetime


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
            # TODO better message with send email if needs acceptance
            # or just hr email if not
            messages.success(request, 'Absence booked successfully, email was sent to proper authorities.')
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


class ManageAbsenceView(View):
    def get(self, request, *args, **kwargs):
        # redirect direct accept/reject links to POST
        if 'accept-submit' in request.GET or 'reject-submit' in request.GET:
            request.POST = request.GET
            return self.post(request, args, kwargs)
        # otherwise, show management panel
        d = date.today()
        month_begin = date(d.year, d.month, 1)
        month_end = date(d.year, d.month, monthrange(d.year, d.month)[1])
        context = {
            'month_begin': dateToString(month_begin),
            'month_end': dateToString(month_end),
            'users': objListToJson(get_user_model().objects.all()),
        }
        if 'absence-id' in request.GET:
            try:
                # TODO maybe we want to allow accepting rejected absences?
                context['accept_absence'] = Absence.objects.get(
                        id=request.GET['absence-id'], status=Absence.PENDING).toDict()
                context['accept_ranges'] = objListToJson(
                        AbsenceRange.objects.filter(absence=request.GET['absence-id']))
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid or already processed absence selected.')
        return render(request, 'planner/manage.html', context)

    def post(self, request, *args, **kwargs):
        try:
            # TODO maybe we want to allow accepting rejected absences?
            absence = Absence.objects.get(id=request.POST['absence-id'], status=Absence.PENDING)
            if not request.user.is_authenticated() or not request.user.is_manager_of(absence.user):
                raise InternalError('Only the leader of team ' + absence.user.team.name +
                        ' can manage this absence.')
            if 'accept-submit' in request.POST:
                absence.accept()
                messages.success(request,
                        'Absence request by ' + absence.user.get_full_name() + ' accepted')
            elif 'reject-submit' in request.POST:
                absence.reject()
                messages.info(request,
                        'Absence request by ' + absence.user.get_full_name() + ' rejected')
            else:
                messages.error(request, 'Invalid request: no decision made.')
        except KeyError:
            messages.error(request, 'Invalid request: no absence given.')
        except ObjectDoesNotExist:
            messages.error(request, 'Invalid or already processed absence selected.')
        except InternalError as e:
            messages.error(request, e.message)
        return HttpResponseRedirect('/')


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


class HolidayRestView(View):
    def get(self, request):
        """ Returns all holidays between given dates"""
        # TODO: ^^ for given users (or holiday calendars?)
        if 'begin' not in request.GET:
            return _make_error_response('begin not specified')
        if 'end' not in request.GET:
            return _make_error_response('end not specified')
        try:
            rbegin = stringToDate(request.GET['begin'])
            rend = stringToDate(request.GET['end'])
        except InternalError as e:
            return _make_error_response(e.message)
        holidays = Holiday.objects.filter(day__gte=rbegin, day__lte=rend)
        return _make_json_response(objListToJson(holidays))


class YearFormView(FormView):
        template_name = 'planner/year_form.html'
        form_class = YearForm
        success_url = '/save_weekends'

        def form_valid(self, form):
            self.request.session['_year'] = date.strftime(form.cleaned_data['year'], '%Y-%m-%d')
            return HttpResponseRedirect('/save_weekends')


def SaveWeekendsView(request):
    date = datetime.strptime(request.session['_year'], '%Y-%m-%d')
    print date.year
    days = Holiday.weekends(date.year)
    holidays = [Holiday(day=day, name=name) for (day,name) in days]
    Holiday.objects.bulk_create(holidays)
    return HttpResponseRedirect('/admin/planner/holiday')
