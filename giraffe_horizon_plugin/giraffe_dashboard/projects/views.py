__author__ = 'omihelic, fbahr'

from horizon import tables
from horizon import tabs

from giraffe_dashboard import client_proxy

from .tables import ProjectsTable
from .tabs import ProjectDetailTabs

# import logging
# logger = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = ProjectsTable
    template_name = 'giraffe_dashboard/projects/index.html'

    def get_data(self):
        projects = client_proxy.get_projects(request=self.request,
                                             params={'details': True})
        for p in projects:
#           count = client_proxy.get_project_instances( \
#                                    request=self.request, \
#                                    project_id=p.uuid, \
#                                    params={'aggregation': 'count'})
#           setattr(p, 'num_instances', count)
            setattr(p, 'num_instances', p.details['num_instances'])

        return projects


class DetailView(tabs.TabView):
    tab_group_class = ProjectDetailTabs
    template_name = 'giraffe_dashboard/projects/detail.html'

    def get_context_data(self, **kwargs):
        # call base implementation first to get a context
        context = super(DetailView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

#   def post(self, request, *args, **kwargs):
#       # GET and POST requests are handled in the same way
#       return self.get(request, *args, **kwargs)
