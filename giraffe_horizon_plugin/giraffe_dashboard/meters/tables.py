from django.utils.translation import ugettext as _

from horizon import tables


class MetersTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('ID'))
    name = tables.Column('name', verbose_name=_('Name'))
    description = tables.Column('description', verbose_name=_('Description'))
    unit_name = tables.Column('unit_name', verbose_name=_('Unit'))
    data_type = tables.Column('data_type', verbose_name=_('Data Type'))
    type = tables.Column('type', verbose_name=_('Meter Type'))

    class Meta:
        name = "meters"
        verbose_name = _("Meters")
#        row_actions = (ViewHost,)
