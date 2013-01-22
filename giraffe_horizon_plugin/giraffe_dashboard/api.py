from horizon.api.base import APIResourceWrapper
from horizon.api.base import APIDictWrapper


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
