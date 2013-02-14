import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon import forms as horizon_forms
from horizon import time

from giraffe_dashboard import api
from giraffe_dashboard import forms

LOG = logging.getLogger(__name__)


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
        submitted = False
        if self.request.GET.get('meter', False):
            submitted = True

        host = api.get_host(self.request, self.tab_group.kwargs['host_id'])
        meters = api.get_host_meters(self.request,
                                   self.tab_group.kwargs['host_id'])
        meters = [m for m in meters if m.name.startswith('host')]
        if not host:
            raise exceptions.Http302(reverse(\
                                   'horizon:giraffe_dashboard:hosts:index'))
        today = time.today()
        month = self.request.GET.get('month', today.month)
        year = self.request.GET.get('year', today.year)
        meter_id = self.request.GET.get('meter', meters[0].id if meters
                                                              else None)
        meter = None
        if meter_id:
            for m in meters:
                if int(m.id) == int(meter_id):
                    meter = m
                    break

        form = forms.DateMeterForm(initial={'month': month,
                                            'year': year,
                                            'meter': meter_id},
                                   meters=meters,)

        context = {'submitted': submitted}
        if submitted and meter_id:
            daily_avgs = api.get_host_meter_records_daily_avg(self.request,\
                                           host_id=host.id, meter_id=meter_id,\
                                           year=year, month=month)
            context['graph'] = {'y_data': daily_avgs,
                                'x_data': range(1, len(daily_avgs) + 1)}

        context['host'] = host
        context['form'] = form
        context['meters'] = meters
        context['meter'] = meter
        return context


class HostDetailTabs(tabs.TabGroup):
    slug = "host_details"
    tabs = (OverviewTab, AnalysisTab,)
