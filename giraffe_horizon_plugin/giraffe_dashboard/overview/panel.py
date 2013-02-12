from django.utils.translation import ugettext as _

import horizon
import giraffe_dashboard.dashboard


class OverviewPanel(horizon.Panel):
    name = _("Overview")
    slug = 'overview'
    roles = ('admin',)

giraffe_dashboard.dashboard.GiraffePlugin.register(OverviewPanel)
