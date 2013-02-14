from django.utils.translation import ugettext as _

import horizon
import giraffe_dashboard.dashboard


class MetersPanel(horizon.Panel):
    name = _("Meters")
    slug = 'meters'
    roles = ('admin',)


giraffe_dashboard.dashboard.GiraffePlugin.register(MetersPanel)
