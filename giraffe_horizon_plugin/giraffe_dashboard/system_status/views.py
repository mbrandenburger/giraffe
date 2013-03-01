__author__ = 'omihelic'

'''
Defines one or more views of the panel.

A views can be defined through a class (XyzView) or a method (xyz).
Note: the views are referenced in the urls.py file.
'''

# from django import shortcuts
# def index(request):
#     return shortcuts.render(request, 'giraffe_dashboard/overview/index.html')

from horizon import tables
from horizon.api.base import APIDictWrapper

from giraffe_dashboard import client_proxy

from .database_status.tables import DatabaseStatusTable
from .service_status.tables import ServiceStatusTable

# import logging
# LOG = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    table_classes = (ServiceStatusTable, DatabaseStatusTable)
    template_name = 'giraffe_dashboard/system_status/index.html'
    client = None

    def get_database_status_data(self):
        request = self.request
        project_count = client_proxy.get_projects_count(request)
        host_count = client_proxy.get_hosts_count(request)
        instance_count = client_proxy.get_instances_count(request)
        meter_count = client_proxy.get_meters_count(request)
        record_count = client_proxy.get_records_count(request)
        if record_count:
            record_count = '{0:,}'.format(record_count)
        data = {'id': 1,
                'project_count': project_count,
                'host_count': host_count,
                'instance_count': instance_count,
                'meter_count': meter_count,
                'record_count': record_count}
        return [APIDictWrapper(data)]

    def get_service_status_data(self):
        svc_type = 'REST API'
        svc_host = client_proxy.rest_api_endpoint(self.request)
        svc_status = 'Active' \
                     if   client_proxy.get_root(self.request) \
                     else 'Inactive'
        data = {'id': 1, 'svc_type': svc_type, 'svc_host': svc_host,
                'svc_status': svc_status}
        return [APIDictWrapper(data)]
