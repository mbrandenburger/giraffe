from django.conf.urls.defaults import patterns, url

from .views import IndexView


#urlpatterns = patterns('giraffe_dashboard.overview.views',
#    url(r'^$', 'index', name='index'))

urlpatterns = patterns('giraffe_dashboard.overview.views',
    url(r'^$', IndexView.as_view(), name='index'))
