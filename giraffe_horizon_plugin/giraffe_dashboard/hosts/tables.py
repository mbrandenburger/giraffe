from django.utils.translation import ugettext as _

from horizon import api
from horizon import tables


#class ViewHost(tables.LinkAction):
#    name = "view"
#    verbose_name = _("View")
#    url = "horizon:giraffe:hosts:detail"
#    classes = ("btn-edit",)


class HostsTable(tables.DataTable):
    id = tables.Column('id', link="horizon:giraffe_dashboard:hosts:detail",
                       verbose_name=_('ID'))
    name = tables.Column('name', link="horizon:giraffe_dashboard:hosts:detail",
                         verbose_name=_('Name'))
    activity = tables.Column('activity', verbose_name=_('Latest Activity'))

    class Meta:
        name = "hosts"
        verbose_name = _("Hosts")
#        row_actions = (ViewHost,)
