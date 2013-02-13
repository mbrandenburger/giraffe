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

from horizon import tables
from horizon.api.base import APIDictWrapper
from .tables import BillingTable

from giraffe_dashboard import api


LOG = logging.getLogger(__name__)

my_log = logging.getLogger("giraffe_dashboard")
my_log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler("/opt/giraffe/bin/log/marcus_debug_log")
fh.setFormatter(formatter)
my_log.addHandler(fh)


class IndexView(tables.DataTableView):
    table_class = BillingTable
    template_name = 'giraffe_dashboard/billing/index.html'

    def get_data(self):

        project = self.request.user.tenant_id

        # TODO replace constant month and year
        month = 2
        year = 2013

        calcfactor_byte2gbyte = 1000000000
        calcfactor_ns2hours = 3600000000000

        used_meter_cpu = long(
            api.get_proj_meter_record_montly_total(self.request, project,
                                                   "inst.cpu.time", month,
                                                   year)) / calcfactor_ns2hours
        meter_disk_io_r = long(
            api.get_proj_meter_record_montly_total(self.request, project,
                                                   "inst.disk.io.read.bytes",
                                                   month,
                                                   year)) / calcfactor_byte2gbyte
        meter_disk_io_w = long(
            api.get_proj_meter_record_montly_total(self.request, project,
                                                   "inst.disk.io.write.bytes",
                                                   month,
                                                   year)) / calcfactor_byte2gbyte
        used_meter_disk_io = meter_disk_io_r + meter_disk_io_w

        meter_net_io_r = long(
            api.get_proj_meter_record_montly_total(self.request, project,
                                                   "inst.network.io.incoming.bytes",
                                                   month,
                                                   year)) / calcfactor_byte2gbyte
        meter_net_io_w = long(
            api.get_proj_meter_record_montly_total(self.request, project,
                                                   "inst.network.io.outgoing.bytes",
                                                   month,
                                                   year)) / calcfactor_byte2gbyte
        used_meter_net_io = meter_net_io_r + meter_net_io_w

        free_meter_cpu = 10000
        free_meter_disk_io = 1020
        free_meter_net_io = 1020

        diff_meter_cpu = used_meter_cpu - free_meter_cpu
        diff_meter_disk_io = used_meter_disk_io - free_meter_disk_io
        diff_meter_net_io = used_meter_net_io - free_meter_net_io

        unit_cost_meter_cpu = 0.01
        unit_cost_meter_disk_io = 0.01
        unit_cost_meter_net_io = 0.01

        if diff_meter_cpu <= 0:
            cost_meter_cpu = 0
        else:
            cost_meter_cpu = diff_meter_cpu * unit_cost_meter_cpu

        if diff_meter_disk_io <= 0:
            cost_meter_disk_io = 0
        else:
            cost_meter_disk_io = diff_meter_disk_io * unit_cost_meter_disk_io

        if diff_meter_net_io <= 0:
            cost_meter_net_io = 0
        else:
            cost_meter_net_io = diff_meter_net_io * unit_cost_meter_net_io

        out = [APIDictWrapper(
            {"id": 1, "label": "Amount used", "meter_cpu": used_meter_cpu,
             "meter_disk_io": used_meter_disk_io,
             "meter_net_io": used_meter_net_io}),
               APIDictWrapper(
                   {"id": 2, "label": "Free", "meter_cpu": free_meter_cpu,
                    "meter_disk_io": free_meter_disk_io,
                    "meter_net_io": free_meter_net_io}),
               APIDictWrapper(
                   {"id": 3, "label": "Difference", "meter_cpu": diff_meter_cpu,
                    "meter_disk_io": diff_meter_disk_io,
                    "meter_net_io": diff_meter_net_io}),
               APIDictWrapper({"id": 4, "label": "Cost per Unit",
                               "meter_cpu": unit_cost_meter_cpu,
                               "meter_disk_io": unit_cost_meter_disk_io,
                               "meter_net_io": unit_cost_meter_net_io}),
               APIDictWrapper(
                   {"id": 5, "label": "Costs", "meter_cpu": cost_meter_cpu,
                    "meter_disk_io": cost_meter_disk_io,
                    "meter_net_io": cost_meter_net_io})]

        return out
