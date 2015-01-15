from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.base import View
from django.views.generic.edit import FormView

from planner.forms import RegisterForm
from planner.models import Vacation, AbsenceRange
from planner.utils import InternalError, stringToDate, dateToString


class IndexView(SuccessMessageMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'planner/index.html', context)


class RegisterView(SuccessMessageMixin, FormView):
    form_class = RegisterForm
    template_name = 'planner/register.html'
    success_url = '/'
    success_message = "Account has been created successfully."

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)


class BookVacationView(SuccessMessageMixin, View):

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
        return HttpResponseRedirect('/')

    def validateRanges(self, begins, ends):
        """ Validate date ranges received from user.

        Takes two lists of 'YYYY-MM-DD' strings.
        Returns validated list of date pairs.
        Throws InternalError on errors.
        """
        if not begins or not ends:
            raise InternalError("no absence ranges given")
        if len(begins) != len(ends):
            raise InternalError("begin[] and end[] sizes differ")
        ranges = sorted(zip(map(stringToDate, begins), map(stringToDate, ends)))
        # check dates integrity
        # TODO: would it be nicer to have this in Vacation model validator?
        prev_end = None
        for (begin, end) in ranges:
            if begin > end:
                raise InternalError("Range begin (%s) is after its end (%s)"
                        % (dateToString(begin), dateToString(end)))
            if prev_end and prev_end >= begin:
                raise InternalError("ranges [... - %s] and [%s - ...] overlaps"
                        % (dateToString(prev_end), dateToString(begin)))
            prev_end = end
        return ranges

    def addVacation(self, ranges):
        """ Takes a list of ranges (date pairs) and saves them as a vacation. """
        Vacation.createFromRanges(None, ranges)
        # nothing really to do here

