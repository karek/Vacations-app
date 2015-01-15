from django.conf.urls import patterns, url
from planner import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^book-vacation/$', views.BookVacationView.as_view(), name='book-vacation')
)

