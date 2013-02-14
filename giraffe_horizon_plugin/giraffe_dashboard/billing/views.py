# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Openstack, LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from horizon.api.base import APIDictWrapper
from horizon import forms
from horizon import tables
from horizon import time

from giraffe_dashboard import api

from .tables import BillingTable


LOG = logging.getLogger(__name__)

#my_log = logging.getLogger("giraffe_dashboard")
#my_log.setLevel(logging.DEBUG)
#formatter = logging.Formatter(
#    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh = logging.FileHandler("/opt/giraffe/bin/log/marcus_debug_log")
#fh.setFormatter(formatter)
#my_log.addHandler(fh)


class IndexView(tables.DataTableView):
    table_class = BillingTable
    template_name = 'giraffe_dashboard/billing/index.html'
    _billing_data = None

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        month = self._get_month()
        year = self._get_year()
        if year and month:
            data = self._get_billing_data(year, month)
            total = float(data[4]["meter_cpu"])\
                    + float(data[4]["meter_disk_io"])\
                    + float(data[4]["meter_net_io"])
            context["total_costs"] = '%0.2f' % total
        self.today = time.today()
        initial = {'month': month if month else self.today.month,
                   'year': year if year else self.today.year}
        self.form = forms.DateForm(initial=initial)
        context['form'] = self.form
        return context

    def get_data(self):
        month = self._get_month()
        year = self._get_year()
        if year and month:
            return self._get_billing_data(year, month)
        else:
            return []

    def _get_month(self):
        return self.request.GET.get('month', None)

    def _get_year(self):
        return self.request.GET.get('year', None)

    def _get_billing_data(self, year, month):
        if self._billing_data:
            return self._billing_data

        request = self.request
        project_id = self.request.user.tenant_id
        instances = api.get_project_instances(request, project_id)

        cpu = api.get_instances_records_monthly_sum(request,\
                               instances=instances, meter_id='inst.cpu.time',\
                               month=month, year=year)
        # nanoseconds to hours
        cpu = float(cpu) / 3600000000000 if cpu else 0.0

        disk_r = api.get_instances_records_monthly_sum(request,
                                                     instances=instances,\
                                           meter_id='inst.disk.io.read.bytes',\
                                           month=month, year=year)
        disk_w = api.get_instances_records_monthly_sum(request,
                                                     instances=instances,\
                                          meter_id='inst.disk.io.write.bytes',\
                                          month=month, year=year)
        disk = 0.0
        disk += float(disk_r) if disk_r else 0
        disk += float(disk_w) if disk_w else 0
        disk /= 1024 * 1024 * 1024  # bytes to gigabytes

        net_in = api.get_instances_records_monthly_sum(request,
                                                       instances=instances,\
                                    meter_id='inst.network.io.incoming.bytes',\
                                    month=month, year=year)
        net_out = api.get_instances_records_monthly_sum(request,\
                                                        instances=instances,\
                                    meter_id='inst.network.io.outgoing.bytes',\
                                    month=month, year=year)
        net = 0.0
        net += float(net_in) if net_in else 0
        net += float(net_out) if net_out else 0
        net /= 1024 * 1024 * 1024  # bytes to gigabytes

        free_cpu = 0.0  # in cpu hours
        free_disk = 0.0  # in gigabytes
        free_net = 0.0  # in gigabytes

        price_cpu = 0.01
        price_disk = 0.01
        price_net = 0.01

        diff_cpu = cpu - free_cpu if cpu - free_cpu > 0 else 0
        diff_disk = disk - free_disk if disk - free_disk > 0 else 0
        diff_net = net - free_net if net - free_net > 0 else 0

        cost_cpu = diff_cpu * price_cpu
        cost_disk = diff_disk * price_disk
        cost_net = diff_net * price_net

        data = []
        data.append(APIDictWrapper({"id": 1, "label": "Amount used",
                                    "meter_cpu": '%0.6f' % cpu,
                                    "meter_disk_io": '%0.6f' % disk,
                                    "meter_net_io": '%0.6f' % net}))
        data.append(APIDictWrapper({"id": 2, "label": "Free",
                                    "meter_cpu": '%0.4f' % free_cpu,
                                    "meter_disk_io": '%0.4f' % free_disk,
                                    "meter_net_io": '%0.4f' % free_net}))
        data.append(APIDictWrapper({"id": 3, "label": "Difference",
                                    "meter_cpu": '%0.6f' % diff_cpu,
                                    "meter_disk_io": '%0.6f' % diff_disk,
                                    "meter_net_io": '%0.6f' % diff_net}))
        data.append(APIDictWrapper({"id": 4, "label": "Cost per Unit",
                                    "meter_cpu": '%0.2f' % price_cpu,
                                    "meter_disk_io": '%0.2f' % price_disk,
                                    "meter_net_io": '%0.2f' % price_net}))
        data.append(APIDictWrapper({"id": 5, "label": "Costs",
                                    "meter_cpu": '%0.2f' % cost_cpu,
                                    "meter_disk_io": '%0.2f' % cost_disk,
                                    "meter_net_io": '%0.2f' % cost_net}))
        self._billing_data = data
        return self._billing_data
