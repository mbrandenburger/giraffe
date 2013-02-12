import logging

from horizon.api.base import APIResourceWrapper
from horizon.api.base import APIDictWrapper

from giraffe.client.api import GiraffeClient


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
        return [APIDictWrapper(m) for m in giraffeclient(request).\
                                                    get_host_meters(host_id)]
    except Exception:
        return []


def get_meters_count(request):
    try:
        return giraffeclient(request).get_meters({'aggregation': 'count'})
    except Exception as e:
        LOG.exception(e)
        return None
