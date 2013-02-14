from horizon import tables


class DatabaseStatusTable(tables.DataTable):
    col_project_count = tables.Column('project_count',
                                      verbose_name=_("# Projects"))
    col_host_count = tables.Column('host_count',
                                   verbose_name=_("# Hosts"))
    col_instance_count = tables.Column('instance_count',
                                      verbose_name=_("# Instances"))
    col_meter_count = tables.Column('meter_count',
                                    verbose_name=_("# Meters"))
    col_record_count = tables.Column('record_count',
                                     verbose_name=_('# MeterRecords'))

    class Meta:
        name = "database_status"
        verbose_name = _("Database Status")
