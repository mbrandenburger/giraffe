__author__ = 'omihelic'

from giraffe_dashboard import client_proxy

from horizon import tables

from .tables import MetersTable

import logging
LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = MetersTable
    template_name = 'giraffe_dashboard/meters/index.html'

    def get_data(self):
        return client_proxy.get_meters(self.request)
