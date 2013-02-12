__author__ = 'fbahr'

"""
Usage:
    from giraffe.client.api import GiraffeClient
    gc = GiraffeClient(<auth_token>)
    or
    gc = GiraffeClient()
    gc.auth_token = <auth_token>
    or
    gc = GiraffeClient(username=<username>, password=<password>, ...)

    ^ Note that up to now, missing params [like endpoint etc.] are collected
      from giraffe.cfg - maybe it's a good idea to omit this feature, though.

    gc.get_root()
    > "Welcome...
    hosts = gc.get_hosts()
    > (list of dicts representing host records)
    or
    hosts = gc.get_hosts().as_(Host)
    > (list of Host objects)
    etc.

Additional remarks:
    In case of connection failures, a requests.exceptions.ConnectionError
    is raised; in case of bad requests (HTTP 40x codes), a
    requests.exceptions.HTTPError.
"""

import requests  # < requests 0.14.2

from giraffe.common.config import Config
from giraffe.common.url_builder import URLBuilder
from giraffe.common.auth import AuthProxy
from giraffe.service.db import Base  # .., Host, Meter, MeterRecord
from giraffe.client.formatter import DEFAULT_FORMATTERS, FormattableObject

import logging
logger = logging.getLogger("client")
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# logger.addHandler(ch)


class GiraffeClient(object):

    def __init__(self, auth_token=None, \
        #              username=None, \
        #              password=None, \
        #              tenant_name=None, \
        #              tenant_id=None, \
        #              protocol=None, \
        #              endpoint=None, \
        #              auth_url=None, \
                       **kwargs):
        """
        Creates a new GiraffeClient instance:
        - if auth_token is not None, auth_token is used to authenticate
          client requests
        - alternatively, credentials (username, password, tenant_id, etc.)
          to be used to authenticate client requests can be passed to
          __init__() via named parameters
        """

        # [DELETED]
        # - right now, also a fallback to giraffe.cfg is implemented (but not
        #   to env. variables)
        self.config = Config('giraffe.cfg')

        if not auth_token:
            _username = kwargs.get('username')
            #                      , self.config.get('client', 'user'))
            _password = kwargs.get('password')
            #                      , self.config.get('client', 'pass'))
            _tenant_name = kwargs.get('tenant_name')
            #                         , self.config.get('client', 'tenant_name'))
            _tenant_id = kwargs.get('tenant_id')
            #                       , self.config.get('client', 'tenant_id'))
            _auth_url = kwargs.get('auth_url', \
                                   self.config.get('auth', 'auth_url'))

            auth_token = AuthProxy.get_token(username=_username,
                                             password=_password,
                                             tenant_name=_tenant_name,
                                             tenant_id=_tenant_id,
                                             auth_url=_auth_url)

        self.auth_header = dict([('X-Auth-Token', auth_token)])
        #@[fbahr] - TODO: Exception handling

        self.protocol = kwargs.get('protocol', 'http')
        self.endpoint = kwargs.get('endpoint')
        if not self.endpoint:
            host = kwargs.get('host', self.config.get('client', 'host'))
            port = kwargs.get('port', self.config.get('client', 'port'))
            self.endpoint = ':'.join((host, port))

    @property
    def auth_token(self):
        return self.auth_header['X-Auth-Token']

    @auth_token.setter
    def auth_token(self, auth_token):
        self.auth_header['X-Auth-Token'] = auth_token

    def _get(self, path, params=None):
        # ---------------------------------------------------------------------
        class ResultSet(tuple):
            def __new__(cls, first=(), *next):
                if isinstance(first, (list)) and not next:
                    return tuple.__new__(cls, tuple(first))
                else:
                    return tuple.__new__(cls, (first, ) + next)

            def as_(self, cls, **kwargs):
                """
                Returns a tuple of cls-serialized representations of
                ResultSet elements; cls is supposed to be a db.Base or
                formatter.FormattableObject subclass.
                """
                if not issubclass(cls, (Base, FormattableObject)):
                    raise TypeError('Expects FormattableObject.')

                if not self:  # ...not len(self), or: len(self) == 0
                    return None

                formatter = kwargs.get('formatter', DEFAULT_FORMATTERS.get(cls))

                return tuple(formatter.serialize(elem) for elem in self)
        # end of class _ResultSet ---------------------------------------------

        url = URLBuilder.build(self.protocol, self.endpoint, path, params)
        logger.debug('Query: %s' % url)
        response = requests.get(url, headers=self.auth_header)
        logger.debug('HTTP response status code: %s' % response.status_code)
        response.raise_for_status()

        return ResultSet(response.json) \
                   if isinstance(response.json, (tuple, list, dict)) \
                   else response.json
        # ...was:  else response.text

    def get_root(self, params=None):
        """
        Welcome ...
        """
        path = '/'
        return self._get(path, None)

    def get_hosts(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            {'id': '<server_id (int)>',
             'name': '<server_name>'}
        dicts
        """
        path = '/hosts'
        return self._get(path, params)  # .as_(Host)

    def get_host(self, host, params=None):
        """
        WARNING: get_host - like every other API method - returns a _tuple_
          (ResultSet), despite containing only a single element; the same
          applies to ResultSet::as_().
        """
        path = '/'.join(['/hosts', str(host)])
        return self._get(path, params)  # .as_(Host)

    def get_host_meters(self, host, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            {'id': '<meter_id (int)>',
             'name': '<meter_name (string)>',
             'description': '<description>',
             'unit_name': '[seconds|..]',
             'data_type': '[float|..]'}
        dicts
        """
        path = '/'.join(['/hosts', str(host), 'meters'])
        return self._get(path, params)  # .as_(Meter)

    def get_host_meter_records(self, host, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            {'id': '<record_id (int)',
             'host_id': '<host_id (string)>',
             'resource_id': '<intance_id (string)>',
             'project_id': '...',
             'user_id': '...',
             'meter_id': '... (int)',
             'timestamp': '2013-01-27 08:46:35',
             'value': '...',
             'duration': '... (int)',
             'signature': '...'}
        dicts
        """
        path = '/'.join(['/hosts', str(host), 'meters', str(meter), 'records'])
        return self._get(path, params)  # .as_(MeterRecord)

    def get_instances(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            ...
        dicts
        """
        path = '/instances'
        return self._get(path, params)

    def get_instance(self, inst, params=None):
        """
        WARNING: get_host - like every other API method - returns a _tuple_
          (ResultSet), despite containing only a single element; the same
          applies to ResultSet::as_().
        """
        path = '/'.join(['/instances', str(inst)])
        raise NotImplementedError()

    def get_inst_meters(self, inst, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meters }
        dicts
        """
        path = '/'.join(['/instances', str(inst), 'meters'])
        raise NotImplementedError()

    def get_inst_meter_records(self, inst, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/instances', str(inst), 'meters', str(meter), 'records'])
        return self._get(path, params)  # .as_(MeterRecord)

    def get_projects(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            ...
        dicts
        """
        path = '/projects'
        return self._get(path, params)

    def get_project(self, proj, params=None):
        """
        WARNING: get_host - like every other API method - returns a _tuple_
          (ResultSet), despite containing only a single element; the same
          applies to ResultSet::as_().
        """
        path = '/'.join(['/projects', str(proj)])
        return self._get(path, params)

    def get_proj_meters(self, proj, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meters }
        dicts
        """
        path = '/'.join(['/projects', str(proj), 'meters'])
        return self._get(path, params)  # .as_(Meter)

    def get_proj_meter_records(self, proj, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/projects', str(proj), 'meters', str(meter), 'records'])
        return self._get(path, params)  # .as_(MeterRecord)

    def get_users(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            ...
        dicts
        """
        path = '/users'
        return self._get(path, params)

    def get_user_meter_records(self, user, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/users', str(user), 'meters', str(meter), 'records'])
        return self._get(path, params)  # .as_(MeterRecord)

    def get_meters(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            {'id': '<meter_id (int)>',
             'name': '<meter_name (string)>',
             'description': '<description>',
             'unit_name': '[seconds|..]',
             'data_type': '[float|..]'}
        dicts
        """
        path = '/meters'
        return self._get(path, params)  # .as_(Meter)

    def get_meter(self, meter, params=None):
        """
        WARNING: get_host - like every other API method - returns a _tuple_
          (ResultSet), despite containing only a single element; the same
          applies to ResultSet::as_().
        """
        path = '/'.join(['/meters', str(meter)])
        return self._get(path, params)  # .as_(Meter)

    def get_records(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/records'
        return self._get(path, params)  # .as_(MeterRecord)

    def get_record(self, record, params=None):
        """
        WARNING: get_host - like every other API method - returns a _tuple_
          (ResultSet), despite containing only a single element; the same
          applies to ResultSet::as_().
        """
        path = '/'.join(['/records', str(record)])
        return self._get(path, params)  # .as_(MeterRecord)
