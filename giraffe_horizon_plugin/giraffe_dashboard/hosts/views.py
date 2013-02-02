import logging

from django.contrib import messages
from django.views import generic
from horizon import api
from horizon import forms
from horizon import tables
from horizon import tabs

from .tables import HostsTable
from .tabs import HostDetailTabs

from horizon.api.base import APIDictWrapper


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = HostsTable
    template_name = 'giraffe_dashboard/hosts/index.html'

    def get_data(self):
        return [APIDictWrapper({'id': 600,
                                'name': 'fake_host',
                                'activity': '2013-02-01 12:13:14'})]
#        try:
#            hosts = []
#        except:
#            hosts = []
#            LOG.exception("ClientException in hosts index")
#        return hosts


class DetailView(tabs.TabView):
    tab_group_class = HostDetailTabs
    template_name = 'giraffe_dashboard/hosts/detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DetailView, self).get_context_data(**kwargs)
        return context
