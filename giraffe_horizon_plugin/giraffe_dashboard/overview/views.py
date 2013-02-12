'''
Defines one or more views of the panel.

A views can be defined through a class (XyzView) or a method (xyz).
Note: the views are referenced in the urls.py file.
'''

#import logging
#LOG = logging.getLogger(__name__)
#from django.contrib import messages
#from django.views import generic
#from horizon import api
#from horizon import forms
#from horizon import tables
#from .tables import HostsTable

#from django import shortcuts
#def index(request):
#    return shortcuts.render(request, 'giraffe_dashboard/overview/index.html')

from horizon import tables
from horizon.api.base import APIDictWrapper

from giraffe_dashboard import api

from .database_status.tables import DatabaseStatusTable
from .service_status.tables import ServiceStatusTable


class IndexView(tables.MultiTableView):
    table_classes = (ServiceStatusTable, DatabaseStatusTable)
    template_name = 'giraffe_dashboard/overview/index.html'
    client = None

    def get_database_status_data(self):
        data = {'id': 1,
               'host_count': api.get_hosts_count(self.request),
               'meter_count': api.get_meters_count(self.request),
               'record_count': 'TODO'}
        return [APIDictWrapper(data)]

    def get_service_status_data(self):
        data = {'id': 1, 'svc_type': 'REST API',
                         'svc_host': api.rest_api_endpoint(self.request),
                         'svc_status': 'Active' if api.get_root(self.request)
                                                else 'Inactive'}
        return [APIDictWrapper(data)]
