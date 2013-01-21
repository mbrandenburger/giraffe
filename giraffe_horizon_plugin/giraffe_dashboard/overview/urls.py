from django.conf.urls.defaults import patterns, url

#from .views import IndexView, DetailView


urlpatterns = patterns('giraffe_dashboard.overview.views',
    url(r'^$', 'index', name='index'))
