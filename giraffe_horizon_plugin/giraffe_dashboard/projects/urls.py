__author__ = 'omihelic, fbahr'

from django.conf.urls.defaults import patterns, url

from .views import IndexView, DetailView


urlpatterns = patterns(
    'giraffe.projects.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<project_id>[^/]+)/$', DetailView.as_view(), name='detail'),
)
