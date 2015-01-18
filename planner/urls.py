from django.conf.urls import patterns, url
from planner import views

urlpatterns = patterns(
    # application urls:
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^plan-absence/$', views.PlanAbsenceView.as_view(), name='plan-absence'),
    # urls for ajax calls (returning jsons):
    url(r'^get-all-users/$', views.get_all_users, name='get-all-users'),
    url(r'^get-ranges-between/$', views.get_ranges_between, name='get-ranges-between')
)

