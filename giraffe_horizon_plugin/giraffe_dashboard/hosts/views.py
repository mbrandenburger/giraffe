import logging

from horizon import tables
from horizon import tabs

from giraffe_dashboard import api

from .tables import HostsTable
from .tabs import HostDetailTabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = HostsTable
    template_name = 'giraffe_dashboard/hosts/index.html'

    def get_data(self):
        return api.get_hosts(self.request)


class DetailView(tabs.TabView):
    tab_group_class = HostDetailTabs
    template_name = 'giraffe_dashboard/hosts/detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DetailView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
#        if request.is_ajax():
#            context['hide'] = True
#            context['x_values'] = range(1, 31)
#            self.template_name = ('giraffe_dashboard/hosts/_'\
#                                  'analysis_data.html')
        return self.render_to_response(context)

#    def post(self, request, *args, **kwargs):
#        # GET and POST handling are the same
#        return self.get(request, *args, **kwargs)
