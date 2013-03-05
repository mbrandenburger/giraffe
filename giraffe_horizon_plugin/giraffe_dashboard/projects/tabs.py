__author__ = 'omihelic, fbahr'

import calendar

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon import forms as horizon_forms
from horizon import time

from giraffe_dashboard import client_proxy
from giraffe_dashboard import forms

import logging
LOG = logging.getLogger(__name__)


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = 'giraffe_dashboard/projects/_detail_overview.html'

    def get_context_data(self, request):
        project = client_proxy.get_projects(self.request,
                                            self.tab_group.kwargs['project_id'])
        if not project:
            raise exceptions.Http302(reverse('horizon:giraffe_dashboard'
                                             ':projects:index'))

#        project_meters = client_proxy.get_host_meters( \
#                                      self.request, \
#                                      self.tab_group.kwargs['project_id'])
#
#        return {'project': project, 'meters': project_meters}

        return {}


class AnalysisTab(tabs.Tab):
    name = _("Analysis")
    slug = "analysis"
    template_name = 'giraffe_dashboard/projects/_detail_analysis.html'

    def get_context_data(self, request):
#        submitted = self.request.GET.get('meter', None) is not None
# 
#        host = client_proxy.get_host(self.request, self.tab_group.kwargs['host_id'])
#        if not host:
#            raise exceptions.Http302(reverse('horizon:giraffe_dashboard'
#                                             ':hosts:index'))
# 
#        # @[fbahr] - TODO: make /hosts/hid/meters return only host meters?!
#        meters = [meter \
#                  for meter in client_proxy.get_host_meters( \
#                                       self.request, \
#                                       self.tab_group.kwargs['host_id']) \
#                  if meter.name.startswith('host')]
# 
#        today = time.today()
#        month = self.request.GET.get('month', today.month)
#        day = self.request.GET.get('day', None)
#        year = self.request.GET.get('year', today.year)
# 
#        meter_id = self.request.GET.get('meter', meters[0].id if meters else None)
#        meter = next(m for m in meters if int(m.id) == int(meter_id)) \
#                    if meter_id \
#                    else None
# 
#        form = forms.DateMeterForm(initial={'month': month,
#                                            'year': year,
#                                            'day': 0,
#                                            'meter': meter_id},
#                                   meters=meters)
# 
#        context = {'submitted': submitted}
#        if submitted and meter_id:
#            avgs = client_proxy.get_host_meter_records_avg(request=self.request,
#                                                  host_id=host.id,
#                                                  meter_id=meter_id,
#                                                  year=year,
#                                                  month=month,
#                                                  day=int(day))
# 
#            ticks = 25 if day else (calendar.monthrange(*map(int, (year, month)))[1] + 1)
# 
#            context['graph'] = {'y_data': avgs,
#                                'x_data': range(1, ticks)}
# 
#        context['form'] = form
#        context['meters'] = meters
#        context['host'] = host
#        context['meter'] = meter

        context = {}
        return context


class ProjectDetailTabs(tabs.TabGroup):
    slug = "project_details"
    tabs = (OverviewTab, AnalysisTab,)
