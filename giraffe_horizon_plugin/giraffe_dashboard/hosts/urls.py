from django.conf.urls.defaults import patterns, url

from .views import IndexView, DetailView


urlpatterns = patterns('giraffe.hosts.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^(?P<host_id>[^/]+)/$', DetailView.as_view(), name='detail'),
)
