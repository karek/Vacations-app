from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import FormView
from planner.forms import RegisterForm


def index(request):
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