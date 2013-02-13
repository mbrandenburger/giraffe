import calendar

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon import forms
from horizon.api.base import APIDictWrapper

from giraffe_dashboard import api
from giraffe_dashboard import forms


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = 'giraffe_dashboard/hosts/_detail_overview.html'

    def get_context_data(self, request):
        host = api.get_host(self.request, self.tab_group.kwargs['host_id'])
        host_meters = api.get_host_meters(self.request,
                                   self.tab_group.kwargs['host_id'])
        if not host:
            raise exceptions.Http302(reverse(\
                                   'horizon:giraffe_dashboard:hosts:index'))
        return {'host': host, 'meters': host_meters}


class AnalysisTab(tabs.Tab):
    name = _("Analysis")
    slug = "analysis"
    template_name = 'giraffe_dashboard/hosts/_detail_analysis.html'

    def get_context_data(self, request):
        context = {}
        host = api.get_host(self.request, self.tab_group.kwargs['host_id'])
        host_meters = api.get_host_meters(self.request,
                                   self.tab_group.kwargs['host_id'])
        if not host:
            raise exceptions.Http302(reverse(\
                                   'horizon:giraffe_dashboard:hosts:index'))
        form = forms.HostAnalysisForm(self.request.GET, meters=host_meters)

        try:
            month = self.request.GET['month']
            year = self.request.GET['year']
            meter_id = self.request.GET['meter']
            daily_avgs = api.get_host_meter_records_daily_avg(host.id,
                                                              meter_id,
                                                              year, month)
            context['graph'] = {'data': daily_avgs}
        except Exception:
            pass

        context['host'] = host
        context['form'] = form
        context['meters'] = host_meters
        return context


class HostDetailTabs(tabs.TabGroup):
    slug = "host_details"
    tabs = (OverviewTab, AnalysisTab,)
