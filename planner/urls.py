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
    # urls for ajax calls (returning jsons):
    url(r'^user/$', views.UserRestView.as_view(), name='user'),
    url(r'^range/$', views.RangeRestView.as_view(), name='range'),
)

