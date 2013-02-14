from django.conf.urls.defaults import patterns, url

from .views import IndexView


urlpatterns = patterns('giraffe.hosts.views',
    url(r'^$', IndexView.as_view(), name='index'),
)
