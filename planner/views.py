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
from planner.forms import RegisterForm, YearForm, TeamsForm
from planner.models import Absence, AbsenceRange, Holiday, AbsenceKind, Team
from planner.utils import InternalError, stringToDate, dateToString, objToJson, objListToJson
from datetime import datetime


def generate_main_context():
    d = date.today()
    month_begin = date(d.year, d.month, 1)
    month_end = date(d.year, d.month, monthrange(d.year, d.month)[1])
    teamsForm = TeamsForm()
    teams = Team.objects.all()
    teamsForm.fields['teams'].choices = [(x.id, x) for x in Team.objects.all()]
    return {
        'month_begin': dateToString(month_begin),
        'month_end': dateToString(month_end),
        'users': objListToJson(get_user_model().objects.all()),
        'absence_kinds': AbsenceKind.objects.all(),
        'teamsForm': teamsForm,
        'teams': teams
    }


class IndexView(View):
    def get(self, request, *args, **kwargs):
        context = generate_main_context()
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
    next_page = request.GET.get('next', request.POST.get('next', '/'))
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
            absence_kind = request.POST.get('absence_kind')
            self.addVacation(request.user, ranges, absence_kind)
            # TODO better message with send email if needs acceptance
            # or just hr email if not
            messages.success(request, 'Absence booked successfully, email was sent to proper authorities.')
        except InternalError as e:
            messages.error(request, e.message)
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
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

    def addVacation(self, user, ranges, absence_kind):
        """ Takes a list of ranges (date pairs) and saves them as a vacation.
        
        AbsenceRange's clean() checks if the ranges are valid and not intersecting (with themselves
        nor with previous user's absences). """
        Absence.createFromRanges(user, ranges, absence_kind)
        # nothing really to do here


class ManageAbsenceView(View):
    
    template = 'planner/manage.html'

    def get(self, request, *args, **kwargs):
        # unless management succeeds, we go to the same page
        self.destination = request.path
        # prepare data for management panel
        self.context = generate_main_context()
        if 'absence-id' in request.GET:
            try:
                absence = Absence.objects.get(id=request.GET['absence-id'], status=Absence.PENDING)
                self.handle_absence_management(request, absence)
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid or already processed absence selected.')
        return render(request, self.template, self.context)

    def handle_absence_management(self, request, absence):
        # process Accept/Reject request if any
        if 'accept-submit' in request.GET or 'reject-submit' in request.GET:
            try:
                self.accept_reject_absence(request, absence) # throws on error
                return
            except InternalError as e:
                messages.error(request, e.message)
        elif not request.user.is_authenticated():
            messages.warning(request, 'View-only mode, log in to make any changes.')
        # otherwise, or on processing error, prepare the management panel
        self.context['accept_absence'] = absence.toDict()
        self.context['accept_ranges'] = objListToJson(
                AbsenceRange.objects.filter(absence=request.GET['absence-id']))

    def accept_reject_absence(self, request, absence):
        """ Method for handling Accept/Reject requests.
        
        Expects request data in GET.
        Returns if the operation succeeded, otherwise raises InternalError. """
        if not request.user.is_authenticated():
            raise InternalError(
                    'Log in now to commit your changes to request from %s.'
                    % absence.user.get_full_name())
        if not request.user.is_manager_of(absence.user):
            raise InternalError(
                    'Only the leader of team %s can manage this absence.'
                    % absence.user.team.name)
        if 'accept-submit' in request.GET:
            absence.accept()
            messages.success(
                    request,
                    'Absence request by %s accepted' % absence.user.get_full_name())
            return
        elif 'reject-submit' in request.GET:
            absence.reject()
            messages.info(
                    request,
                    'Absence request by %s rejected' % absence.user.get_full_name())
            return
        else:
            messages.error(request, 'Invalid request: no decision made.')


def _make_json_response(data):
    return HttpResponse(data, content_type='application/json')


def _make_error_response(msg):
    return HttpResponseBadRequest(msg, content_type='text/plain')


class UserRestView(View):
    def get(self, request):
        """ Returns all users as array of json objects. """
        return _make_json_response(objListToJson(get_user_model().objects.all()))


class TeamRestView(View):
    def get(self, request):
        """ Returns all users as array of json objects. """
        return _make_json_response(objListToJson(Team.objects.all()))


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


class AbsenceRestView(View):
    def get(self, request):
        """ Returns all absences (without ranges) matching requested parameters:
         * user id
         * team id
         * status
        Filter by dates is not yet needed.
        """
        absences = Absence.objects.filter()
        if 'user-id' in request.GET:
            absences = absences.filter(user__id=request.GET['user-id'])
        if 'team-id' in request.GET:
            absences = absences.filter(user__team__id=request.GET['team-id'])
        if 'status' in request.GET:
            absences = absences.filter(status=request.GET['status'])
        return _make_json_response(objListToJson(absences.order_by('dateCreated', 'user')))


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
    days = Holiday.weekends(date.year)
    holidays = [Holiday(day=day, name=name) for (day,name) in days]
    Holiday.objects.bulk_create(holidays)
    return HttpResponseRedirect('/admin/planner/holiday')
