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
from planner.models import Absence, AbsenceRange, Holiday, AbsenceKind
from planner.utils import InternalError, stringToDate, dateToString, objToJson, objListToJson
from datetime import datetime


def generate_main_context():
    d = date.today()
    month_begin = date(d.year, d.month, 1)
    month_end = date(d.year, d.month, monthrange(d.year, d.month)[1])
    return {
        'month_begin': dateToString(month_begin),
        'month_end': dateToString(month_end),
        'users': objListToJson(get_user_model().objects.all()),
        'absence_kinds': AbsenceKind.objects.all()
    }


class IndexView(View):
    def get(self, request, *args, **kwargs):
        self.context = generate_main_context()
        if 'edit-absence-id' in request.GET:
            try:
                absence = Absence.objects.get(
                        id=request.GET['edit-absence-id'], status=Absence.PENDING)
                self.context['edit_absence'] = absence
                handle_absence_edit(request, absence) # throws on error
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid or already accepted absence selected.')
            except InternalError as e:
                messages.error(request, e.message)
        return render(request, 'planner/index.html', self.context)

    def handle_absence_edit(self, request, absence):
        if not request.user.is_authenticated():
            raise InternalError('Log in now to edit your absence.')
        if request.user.id != absence.user_id:
            raise InternalError('Only absence\'s owner can edit it.')
        self.context['edit_absence'] = absence


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
            kind = AbsenceKind.objects.get(id=request.POST['absence_kind'])
            if 'edit-submit' in request.POST:
                new_abs = self.handle_edit_absence(request, ranges, kind) # throws on error
                message = 'Absence edited successfully, '
            else:
                new_abs = self.handle_add_absence(request, ranges, kind) # throws on error
                message = 'Absence planned successfully, '
            if new_abs.kind.require_acceptance:
                message += 'acceptance request was send to the team leader.'
            else:
                message += 'no further confirmation needed.'
            messages.success(request, text)
        except InternalError as e:
            messages.error(request, e.message)
        except ValidationError as e:
            messages.error(request, '\n'.join(e.messages))
        except ObjectDoesNotExist:
            messages.error(request, 'Invalid absence kind.')
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

    def handle_add_absence(self, request, ranges, absence_kind):
        """ Takes a list of ranges (date pairs) and saves them as a vacation.
        
        AbsenceRange's clean() checks if the ranges are valid and not intersecting (with themselves
        nor with previous user's absences). """
        return Absence.createFromRanges(request.user, ranges, absence_kind)

    def handle_edit_absence(self, request, ranges, absence_kind):
        try:
            old_absence = Absence.objects.get(
                    id=request.POST['edit-absence-id'], status=Absence.PENDING)
            if not request.user.is_authenticated() or request.user.id != absence.user_id:
                raise InternalError('Only absence\'s owner can edit it.')
            return old_absence.editFromRanges(ranges, absence_kind)
        except ObjectDoesNotExist:
            raise InternalError('Invalid or already accepted absence selected.')


class ManageAbsenceView(View):
    
    template = 'planner/manage.html'

    def get(self, request, mode='manager', *args, **kwargs):
        # prepare data for management panel
        self.context = generate_main_context()
        self.context['manage_mode'] = mode
        if 'absence-id' in request.GET:
            try:
                # user can review his pending and accepted absences,
                # manager only his team's pending ones
                if mode == 'selfcare':
                    statuses = [Absence.PENDING, Absence.ACCEPTED, ]
                else:
                    statuses = [Absence.PENDING, ]
                absence = Absence.objects.get(id=request.GET['absence-id'], status__in=statuses)
                self.handle_absence_management(request, absence)
            except ObjectDoesNotExist:
                messages.error(request, 'Invalid or already processed absence selected.')
        return render(request, self.template, self.context)

    def handle_absence_management(self, request, absence):
        # process Accept/Reject request if any
        try:
            if 'accept-submit' in request.GET or 'reject-submit' in request.GET:
                self.accept_reject_absence(request, absence) # throws on error
                return
            elif 'cancel-submit' in request.GET:
                self.cancel_absence(request, absence) # throws on error
                return
            elif not request.user.is_authenticated():
                messages.warning(request, 'View-only mode, log in to make any changes.')
        except InternalError as e:
            messages.error(request, e.message)
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

    def cancel_absence(self, request, absence):
        """ Method for handling Cancel/Delete requests. """
        if not request.user.is_authenticated():
            raise InternalError('Log in now to confirm absence cancellation.')
        if request.user != absence.user:
            raise InternalError('Only absence\'s owner can cancel it.')
        absence.cancel()
        messages.success(request, 'Absence cancelled.')


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


class AbsenceRestView(View):
    def get(self, request):
        """ Returns all absences (without ranges) matching requested parameters:
         * id
         * user-id
         * team-id
         * status (can be a comma-separated list)
         * date-at-least
         * date-at-most
         * date-not-before
         * date-not-after
        All dates should be 'YYYY-MM-DD'.
        """
        absences = Absence.objects.filter()
        if 'id' in request.GET:
            absences = absences.filter(id=request.GET['id'])
        if 'user-id' in request.GET:
            absences = absences.filter(user__id=request.GET['user-id'])
        if 'team-id' in request.GET:
            absences = absences.filter(user__team__id=request.GET['team-id'])
        if 'status' in request.GET:
            statuses = map(int, request.GET['status'].split(','))
            absences = absences.filter(status__in=statuses)
        if 'date-at-least' in request.GET:
            absences = absences.filter(
                    absencerange__end__gt=stringToDate(request.GET['date-at-least']))
        if 'date-at-most' in request.GET:
            absences = absences.filter(
                    absencerange__begin__lte=stringToDate(request.GET['date-at-most']))
        if 'date-not-before' in request.GET:
            absences = absences.exclude(
                    absencerange__begin__lt=stringToDate(request.GET['date-not-before']))
        if 'date-not-after' in request.GET:
            absences = absences.exclude(
                    absencerange__end__gt=stringToDate(request.GET['date-not-after']))
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
