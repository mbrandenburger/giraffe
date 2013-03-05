__author__ = 'omihelic, fbahr'

from django.utils.translation import ugettext as _

from horizon import api
from horizon import tables


class ProjectsTable(tables.DataTable):

    class Meta:
        name = 'projects'
        verbose_name = _('Projects')
#       row_actions = (ViewProject,)

    id = tables.Column('id',
                       link='horizon:giraffe_dashboard:projects:detail',
                       verbose_name=_('ID'))
#   name = tables.Column('name',
#                        link='horizon:giraffe_dashboard:projects:detail',
#                        verbose_name=_('Name'))
#   activity = tables.Column('activity',
#                            verbose_name=_('Latest Activity'))
