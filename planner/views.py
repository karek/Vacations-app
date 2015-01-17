from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import HttpResponseRedirect
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
                # FIXME this should be done with the 'next' parameter in the url
                return HttpResponseRedirect(next_page)
            else:
                messages.error(request, 'Your account is disabled.')
        else:
            messages.error(request, 'Invalid login details.')
    return HttpResponseRedirect(next_page)