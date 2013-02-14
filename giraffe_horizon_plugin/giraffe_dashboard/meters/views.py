import logging

from horizon import tables

from giraffe_dashboard import api

from .tables import MetersTable


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = MetersTable
    template_name = 'giraffe_dashboard/meters/index.html'

    def get_data(self):
        return api.get_meters(self.request)
