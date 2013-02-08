__author__ = 'fbahr'

import requests  # < requests 0.14.2

import json

from giraffe.common.config import Config
from giraffe.common.url_builder import URLBuilder
from giraffe.common.auth import AuthProxy
from giraffe.service.db import Base, Host, Meter, MeterRecord
from giraffe.client.formatter import *


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
        - right now, also a fallback to giraffe.cfg is implemented (but not
          to env. variables)
        """

        self.config = Config('giraffe.cfg')

        if not auth_token:
            _username = kwargs.get('username',
                                   self.config.get('client', 'user'))
            _password = kwargs.get('password',
                                   self.config.get('client', 'pass'))
            _tenant_name = kwargs.get('tenant_name',
                                      self.config.get('client', 'tenant_name'))
            _tenant_id = kwargs.get('tenant_id',
                                    self.config.get('client', 'tenant_id'))
            _auth_url = kwargs.get('auth_url',
                                   self.config.get('client', 'auth_url'))
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

    def _get(self, path, params=None):
        # ---------------------------------------------------------------------
        class ResultSet(tuple):
            def __new__(cls, first=(), *next):
                if isinstance(first, (list)) and not next:
                    return tuple.__new__(cls, tuple(first))
                else:
                    return tuple.__new__(cls, (first, ) + next)

            def _as(self, cls, **kwargs):
                if not issubclass(cls, (Base, FormattableObject)):
                    raise TypeError('Expects FormattableObject.')

                if not self:  # ...not len(self), or: len(self) == 0
                    return None

                formatter = kwargs.get('formatter', DEFAULT_FORMATTERS.get(cls))

                return tuple(formatter.serialize(elem) for elem in self)
        # end of class _ResultSet ---------------------------------------------

        url = URLBuilder.build(self.protocol, self.endpoint, path, params)
        response = requests.get(url, headers=self.auth_header).json

        # @[fbahr] - TODO: exception handling
        return ResultSet(response) \
                   if isinstance(response, (tuple, list, dict)) \
                   else response

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
        return self._get(path, params)  # ._as(Host)

    def get_instances(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            ...
        dicts
        """
        path = '/instances'
        # ...
        raise NotImplementedError()  # ._as(Instance)

    def get_projects(self, params=None): 
        """
        Returns a tuple (actually, a ResultSet instance) of
            ...
        dicts
        """
        path = '/projects'
        # ...
        raise NotImplementedError()  # ._as(Project)

    def get_users(self, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            ...
        dicts
        """
        path = '/users'
        # ...
        raise NotImplementedError()  # ._as(User)

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
        return self._get(path, params)  # ._as(Meter)

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
        path = '/'.join(['/hosts', host, 'meters', meter])
        return self._get(path, params)  # ._as(MeterRecord)

    def get_inst_meter_records(self, inst, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/instances', inst, 'meters', meter])
        return self._get(path, params)  # ._as(MeterRecord)

    def get_proj_meter_records(self, proj, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/projects', proj, 'meters', meter])
        # ...
        raise NotImplementedError()  # ._as(MeterRecord)

    def get_user_meter_records(self, user, meter, params=None):
        """
        Returns a tuple (actually, a ResultSet instance) of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/users', user, 'meters', meter])
        # ...
        raise NotImplementedError()  # ._as(MeterRecord)
