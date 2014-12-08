from django.shortcuts import render

# Create your views here.


def index(request):
    context = {}
    return render(request, 'planner/index.html', context)


def register(request):
    context = {}
    return render(request, 'planner/register.html', context)

