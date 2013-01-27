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
from .database_status.tables import DatabaseStatusTable
from .service_status.tables import ServiceStatusTable

from ..api import ServiceStatus
from horizon.api.base import APIDictWrapper


class IndexView(tables.MultiTableView):
    table_classes = (ServiceStatusTable, DatabaseStatusTable)
    template_name = 'giraffe_dashboard/overview/index.html'

#    def get_data(self):
#        #a = ServiceStatus(id=1, svc_host='uncinus', status='Active')
#        a = APIDictWrapper({'id': 1,
#                            'svc_host': 'uncinus',
#                            'status': 'Active'})
#        #b = APIDictWrapper({'id': 2,
#        #                    'svc_host': 'intortus',
#        #                    'status': 'Inactive'})
#        return [a]

    def get_database_status_data(self):
        return [APIDictWrapper({'id': 1,
                               'host_count': 1,
                               'meter_count': 2,
                               'record_count': 3})]

    def get_service_status_data(self):
        return [APIDictWrapper({'id': 1,
                               'svc_host': 'uncinus',
                               'status': 'Active'})]
