from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import FormView
from planner.forms import RegisterForm


def index(request):
    return render(request, 'planner/index.html', {})


class RegisterView(SuccessMessageMixin, FormView):
    form_class = RegisterForm
    template_name = 'planner/register.html'
    success_url = '/'
    success_message = "Account has been created successfully."

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
                messages.success(request, 'Logged in succesfully. How are you, {0}?'.format(user.first_name))
            else:
                messages.error(request, 'Your account is disabled.')
        else:
            messages.error(request, 'Invalid login details.')
    return HttpResponseRedirect(next_page)


def user(request):
    users = get_user_model().objects.all()
    data = serializers.serialize('json', users, fields=('email', 'first_name', 'last_name'))
    return HttpResponse(data, content_type="application/json")

