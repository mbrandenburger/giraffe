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
from .tables import OverviewTable
from ..api import ServiceStatus
from horizon.api.base import APIDictWrapper


class OverviewView(tables.DataTableView):
    table_class = OverviewTable
    template_name = 'giraffe_dashboard/overview/index.html'

    def get_data(self):
        #a = ServiceStatus(id=1, svc_host='uncinus', status='Active')
        a = APIDictWrapper({'id': 1,
                            'svc_host': 'uncinus',
                            'status': 'Active'})
        #b = APIDictWrapper({'id': 2,
        #                    'svc_host': 'intortus',
        #                    'status': 'Inactive'})
        return [a]
