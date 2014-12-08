from django.shortcuts import render

# Create your views here.
from django.views.generic.edit import FormView
from planner.forms import RegisterForm


def index(request):
    context = {}
    return render(request, 'planner/index.html', context)


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'planner/register.html'
    success_url = '/'

    def form_valid(self, form):
        form.save()
        return super(RegisterView, self).form_valid(form)