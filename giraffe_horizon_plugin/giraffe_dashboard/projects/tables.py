__author__ = 'omihelic, fbahr'

from django.utils.translation import ugettext as _

from horizon import api
from horizon import tables


class ProjectsTable(tables.DataTable):

    class Meta:
        name = 'projects'
        verbose_name = _('Projects')
#       columns = ('project_id', 'num_instances')
#       row_actions = (ViewProject,)

    id = tables.Column('id',
                       link='horizon:giraffe_dashboard:projects:detail',
                       verbose_name=_('Project ID'))
    num_instances = tables.Column('num_instances',
                                  verbose_name=_('# Instances'))
#   activity = tables.Column('activity',
#                            verbose_name=_('Latest Activity'))
