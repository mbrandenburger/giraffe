from django.conf.urls.defaults import patterns, url

from .views import OverviewView


#urlpatterns = patterns('giraffe_dashboard.overview.views',
#    url(r'^$', 'index', name='index'))

urlpatterns = patterns('giraffe_dashboard.overview.views',
    url(r'^$', OverviewView.as_view(), name='index'))
