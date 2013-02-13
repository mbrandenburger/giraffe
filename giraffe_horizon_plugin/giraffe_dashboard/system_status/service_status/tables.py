from horizon import tables


class ServiceStatusTable(tables.DataTable):
    col_type = tables.Column('svc_type', verbose_name=_('Type'))
    col_host = tables.Column('svc_host', verbose_name=_('Host'))
    col_status = tables.Column('svc_status', verbose_name=_('Status'))

    class Meta:
        name = "service_status"
        verbose_name = _("Service Status")
