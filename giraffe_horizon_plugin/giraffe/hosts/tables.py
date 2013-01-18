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

from horizon import api
from horizon import tables


class ViewHost(tables.LinkAction):
    name = "view"
    verbose_name = _("View")
    url = "horizon:giraffe:hosts:detail"
    classes = ("btn-edit",)


class HostsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))

    class Meta:
        name = "hosts"
        verbose_name = _("Hosts")
        row_actions = (ViewHost,)
