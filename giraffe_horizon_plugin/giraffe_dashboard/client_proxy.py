__author__ = 'omihelic, fbahr'

import calendar

from horizon.api.base import APIResourceWrapper
from horizon.api.base import APIDictWrapper

from giraffe.client.api import GiraffeClient
from giraffe.service.db import MeterRecord, Meter

import logging
LOG = logging.getLogger(__name__)


class DictWrapper(APIResourceWrapper):
    '''
    DictWrapper can be used as the base class for dictionaries that should be
    displayed in DataTables.
    Subclasses have to define an _attrs attribute that defines the columns for
    which data is available. As a minimum, an ID has to be defined.
    Example:
    class MyDatum(DictWrapper):
        _attrs = ['id', 'col1', 'col2']
    d = MyDatum(id=.., col1=..., col2=...)

    An alternative is using APIDictWrapper which, however, does not have an
    _attrs Attribute, and instead takes the dictionary as parameter in the
    constructor.
    '''

    def __init__(self, **entries):
        '''
        See:
        http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
        '''
        self.__dict__.update(entries)


class ServiceStatus(DictWrapper):
    _attr = ['svc_host', 'status']


def giraffeclient(request):
    LOG.debug('giraffeclient connection created using token "%s"' %
              request.user.token)
    return GiraffeClient(request.user.token)


def rest_api_endpoint(request):
    try:
        return giraffeclient(request).endpoint
    except Exception as e:
        LOG.exception(e)
        return None


def get_root(request):
    try:
        return giraffeclient(request).get_root()
    except Exception as e:
        LOG.exception(e)
        return None


def get_hosts(request):
    try:
        return [APIDictWrapper(h) for h in giraffeclient(request).get_hosts()]
    except Exception as e:
        LOG.exception(e)
        return []


def get_host(request, host_id):
    try:
        return APIDictWrapper(giraffeclient(request).get_host(host_id)[0])
    except Exception as e:
        LOG.exception(e)
        return None


def get_hosts_count(request):
    try:
        return giraffeclient(request).get_hosts({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None


def get_host_meters(request, host_id):
    try:
        return [APIDictWrapper(m) for m in giraffeclient(request)
                .get_host_meters(host_id)]
    except Exception as e:
        LOG.exception(e)
        return []


def get_host_meter_records_avg(request, host_id, meter_id,
                               year, month, day):
    try:
        year = int(year)
        month = int(month)
        num_days = calendar.monthrange(year, month)[1]
        if not day:
            start_day, end_day = 1, num_days
            aggregation = 'daily_avg'
        else:
            start_day, end_day = (day if day <= num_days else num_days, ) * 2
            aggregation = 'hourly_avg'

        params = {'start_time':
                        '%s-%02d-%02d_00-00-00' % (year, month, start_day),
                  'end_time':
                        '%s-%02d-%02d_23-59-59' % (year, month, end_day),
                  'aggregation':
                        aggregation}

        avgs = giraffeclient(request).get_host_meter_records(host=host_id,
                                                             meter=meter_id,
                                                             params=params)

        return [d if d != 'None' else None for d in avgs]

    except Exception as e:
        LOG.exception(e)
        return None


def get_meters(request):
    try:
        return [APIDictWrapper(m) for m in giraffeclient(request).get_meters()]
    except Exception as e:
        LOG.exception(e)
        return None


def get_meters_count(request):
    try:
        return giraffeclient(request).get_meters({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None


def get_records_count(request):
    try:
        return giraffeclient(request).get_records({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None


def get_projects(request):
    try:
        return [APIDictWrapper({'id': p})
                for p in giraffeclient(request).get_projects()]
    except Exception as e:
        LOG.exception(e)
        return []


def get_project(request, project_id):
    try:
        return giraffeclient(request).get_project(project_id)[0]
    except Exception as e:
        LOG.exception(e)
        return None


def get_project_instances(request, project_id):
    try:
        return giraffeclient(request).get_proj_instances(project_id)
    except Exception as e:
        LOG.exception(e)
        raise e
        return None


def get_projects_count(request):
    try:
        return giraffeclient(request).get_projects({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None


def get_instances_count(request):
    try:
        return giraffeclient(request).get_instances({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None


def get_instances_records_monthly_sum(request, instances, meter_id, month,
                                     year):
    try:
        year = int(year)
        month = int(month)
        days = calendar.monthrange(year, month)[1]
        params = {'aggregation': 'first_last',
                  'start_time': '%s-%02d-01_00-00-00' % (year, month),
                  'end_time': '%s-%02d-%02d_23-59-59' % (year, month, days)}
        total = 0
        for instance in instances:
            result = giraffeclient(request).get_inst_meter_records(\
                                  inst=instance, meter=meter_id, params=params)
            if result and len(result) == 2:
                first = APIDictWrapper(result[0])
                last = APIDictWrapper(result[1])
                total += float(last.value) - float(first.value)
        return total
    except Exception as e:
        LOG.exception(e)
        raise e
        return None
