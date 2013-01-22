from horizon import tables


class OverviewTable(tables.DataTable):
    col_service_host = tables.Column('svc_host', verbose_name=_("Service Host"))
    col_status = tables.Column('status', verbose_name=_("Status"))
