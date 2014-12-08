from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^', include('planner.urls', namespace='planner')),
    url(r'^admin/', include(admin.site.urls)),
)
