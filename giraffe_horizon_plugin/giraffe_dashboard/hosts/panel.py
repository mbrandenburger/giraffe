from django.utils.translation import ugettext as _

import horizon
import giraffe_dashboard.dashboard


class HostsPanel(horizon.Panel):
    name = _("Hosts")
    slug = 'hosts'
    roles = ('admin',)


giraffe_dashboard.dashboard.GiraffePlugin.register(HostsPanel)
