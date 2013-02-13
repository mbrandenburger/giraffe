from django.utils.translation import ugettext as _

import horizon
import giraffe_dashboard.dashboard


class SystemStatusPanel(horizon.Panel):
    name = _("System Status")
    slug = 'system_status'
    roles = ('admin',)

giraffe_dashboard.dashboard.GiraffePlugin.register(SystemStatusPanel)
