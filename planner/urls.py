from django.conf.urls import patterns, url
from planner import views

urlpatterns = patterns(
    # application urls:
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # Example use: login/?next=/register will redirect after logging user in
    url(r'^login/$', views.user_login, name='login'),
    # Example use: logout/?next=/register will redirect after logging user out
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^plan-absence/$', views.PlanAbsenceView.as_view(), name='plan-absence'),
    url(r'^manage-absences/$', views.ManageAbsenceView.as_view(),
        {'mode': 'manager'}, name='manage-absences'),
    url(r'^my-absences/$', views.ManageAbsenceView.as_view(),
        {'mode': 'selfcare'}, name='my-absences'),
    url(r'^save_weekends/$', views.SaveWeekendsView, name='save_weekends'),
    # urls for ajax calls (returning jsons):
    url(r'^user/$', views.UserRestView.as_view(), name='user'),
    url(r'^teams/$', views.TeamRestView.as_view(), name='teams'),
    url(r'^range/$', views.RangeRestView.as_view(), name='range'),
    url(r'^holiday/$', views.HolidayRestView.as_view(), name='holiday'),
    url(r'^absence/$', views.AbsenceRestView.as_view(), name='absence'),
)

