import logging

from horizon.api.base import APIResourceWrapper
from horizon.api.base import APIDictWrapper

from giraffe.client.api import GiraffeClient

import calendar
from giraffe.service.db import MeterRecord, Meter


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
    except Exception:
        return None


def get_root(request):
    try:
        return giraffeclient(request).get_root()
    except Exception:
        return None


def get_hosts(request):
    try:
        return [APIDictWrapper(h) for h in giraffeclient(request).get_hosts()]
    except Exception as e:
        LOG.exception(e)
        return []


def get_hosts_count(request):
    try:
        return giraffeclient(request).get_hosts({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None


def get_host(request, host_id):
    try:
        return APIDictWrapper(giraffeclient(request).get_host(host_id)[0])
    except Exception:
        return None


def get_host_meters(request, host_id):
    try:
        return [APIDictWrapper(m) for m in giraffeclient(request)
                .get_host_meters(host_id)]
    except Exception:
        return []


def get_host_meter_records_daily_avg(request, host_id, meter_id, year, month):
    try:
        year = int(year)
        month = int(month)
        month_days = calendar.monthrange(year, month)[1]
        params = {'start_time': '%s-%02d-01_00-00-00' % (year, month),
                  'end_time': '%s-%02d-%02d_23-59-59' % (year, month,
                                                         month_days),
                  'aggregation': 'daily_avg'}
        return giraffeclient(request).get_host_meter_records(host_id, meter_id,
                                                             params=params)
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


def get_proj_meter_record_montly_total(request, project, meter, month, year):
    """

    :param request:
    :param project:
    :param meter:
    :param month:
    :param year:
    :return:
    """
    try:

        # meter_results = giraffeclient(request).get_meter(meter).as_(Meter)[0]
        #
        # LOG.debug("Meter result: %s" % meter_results)

        month_days = calendar.monthrange(year, month)[1]

        query_params = {'aggregation': 'first_last',
                        'start_time': '%s-%02d-01_00-00-00' % (year, month),
                        'end_time': '%s-%02d-%02d_23-59-59' % (year, month, month_days)}

        all_instances = giraffeclient(request).get_proj_instances(proj=project, params=query_params)

        sum = 0

        # first = {'ordering': 'asc', 'limit': 1,
        #          'start_time': '%s-%02d-01_00-00-00' % (year, month),
        #          'end_time': '%s-%02d-%02d_23-59-59' % (year, month, month_days)}
        #
        # last = {'ordering': 'desc', 'limit': 1,
        #         'start_time': '%s-%02d-01_00-00-00' % (year, month),
        #         'end_time': '%s-%02d-%02d_23-59-59' % (year, month, month_days)}

        for inst_id in all_instances:

            LOG.debug("Instance: %s" % inst_id)

            results = giraffeclient(request).get_inst_meter_records(inst=inst_id, meter=meter, params=query_params)
            # LOG.debug("Result: %s", results)

            if results and len(results) == 2:
                sum += float(results[1]) - float(results[0])


            # count_result = giraffeclient(request).get_inst_meter_records(inst=inst_id, meter=meter, params={"aggregation": "count"})
            #
            # if count_result <= 1:
            #     LOG.debug("No results for instance")
            #     continue
            #
            # if count_result > 1:
            #     first_sum = giraffeclient(request).get_inst_meter_records(inst=inst_id, meter=meter, params=first).as_(MeterRecord)[0].value
            #     last_sum = giraffeclient(request).get_inst_meter_records(inst=inst_id, meter=meter, params=last).as_(MeterRecord)[0].value
            #     sum += last_sum - first_sum
            #     # if tmp_sum == 0:
            #     #     sum += first_sum
            #     # else:
            #     # sum += tmp_sum
            #
            #     LOG.debug("Last: %d First: %d Sum: %d" % (last_sum, first_sum, sum))
            #     continue

        LOG.debug("ENDSum for %s: %d" % (meter,sum))
        return sum


    except Exception as e:
        LOG.exception(e)
        return None
