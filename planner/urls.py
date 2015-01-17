from django.conf.urls import patterns, url
from planner import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^register/$', views.RegisterView.as_view(), name='register'),
                       # Example use: login/?next=/register will redirect after logging user in
                       url(r'^login/$', views.user_login, name='login'),
                       # Example use: logout/?next=/register will redirect after logging user out
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
                       url(r'^user/$', views.user, name='user'),
)

