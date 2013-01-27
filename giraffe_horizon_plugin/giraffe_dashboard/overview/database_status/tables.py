from horizon import tables


class DatabaseStatusTable(tables.DataTable):
    col_host_count = tables.Column('host_count', verbose_name=_("# Host"))
    col_meter_count = tables.Column('meter_count', verbose_name=_("# Meter"))
    col_record_count = tables.Column('record_count', verbose_name=_('# MeterRecord'))

    class Meta:
        name = "database_status"
        verbose_name = _("Database Status")
