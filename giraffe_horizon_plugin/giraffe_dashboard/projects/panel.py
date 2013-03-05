__author__ = 'omihelic, fbahr'

from django.utils.translation import ugettext as _

import horizon
import giraffe_dashboard.dashboard


class ProjectsPanel(horizon.Panel):
    name = _('Projects')
    slug = 'projects'
    roles = ('admin',)


giraffe_dashboard.dashboard.GiraffePlugin.register(ProjectsPanel)
