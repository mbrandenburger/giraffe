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

from django.utils.translation import ugettext as _

from horizon import tables


class BillingTable(tables.DataTable):
    label = tables.Column('label', verbose_name=_('Monthly Bill'))
    meter_cpu = tables.Column('meter_cpu', verbose_name=_(
                                                      'inst.cpu.time [h]'))
    meter_io = tables.Column('meter_io', verbose_name=_(\
                                    'inst.disk.io.(read+write).bytes [Gb]'))

    class Meta:
        name = "Project Billing"
        verbose_name = _("project_billing")
