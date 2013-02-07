__author__ = 'fbahr'

import requests  # < requests 0.14.2

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
                       **kwargs):
        self.auth_url = kwargs.get('auth_url',
                                   self.config.get('client', 'auth_url'))
        self.auth_token = auth_token \
                              if auth_token \
                              else AuthProxy.get_token( \
                                       username=kwargs.get('username'),
                                       password=kwargs.get('password'),
                                       tenant_name=kwargs.get('tenant_name'),
                                       tenant_id=kwargs.get('tenant_id'),
                                       auth_url=self.auth_url)
        self.protocol = kwargs.get('protocol', 'http')
        host = kwargs.get('host', self.config.get('client', 'host'))
        port = kwargs.get('port', self.config.get('client', 'port'))
        self.endpoint = ':'.join((host, port))

    def _get(self, path, params=None):
        # ---------------------------------------------------------------------
        class _ResultSet(object):
            def __init__(self, records):
                self._records = records

            def _as(self, cls, **kwargs):
                if not issubclass(cls, (Base, FormattableObject)):
                    raise TypeError('Expects FormattableObject.')

                if not self._records:
                    return 'Empty result set.'

                if not isinstance(self._records, (tuple, list, dict)):
                    return self._records

                self._formatter = kwargs.get('formatter',
                                             DEFAULT_FORMATTERS.get(cls))

                return tuple(self._formatter.serialize(elem) \
                             for elem in self._records)
        # end of class _ResultSet ---------------------------------------------

        url = URLBuilder.build(self.protocol, self.endpoint, path, params)

        #@[marcus,fbahr]: To be moved to GiraffeClient.__init__? --------------
        # auth_token = AuthProxy.get_token(auth_url=self.auth_url,
        #                                  username=self.username,
        #                                  password=self.password,
        #                                  tenant_name=self.tenant_name)
        # ---------------------------------------------------------------------

        # @[fbahr]: request.get().json returns...? (1. list of dicts, 2. ?) 
        lst = requests.get(url, headers={'X-Auth-Token': self.auth_token}).json
        # @[fbahr] - TODO: exception handling
        return _ResultSet(lst)

    def get_hosts(self, params=None):
        """
        Returns a list of giraffe.service.db.Host objects
        from a list of
            {'id': '<server_id (int)>',
             'name': '<server_name>'}
        dicts
        """
        path = '/hosts'
        return self._get(path, params)._as(Host)

    def get_instances(self, params=None):
        """
        Returns a list of ... objects
        """
        path = '/instances'
        # return self._get(path, params)._as(Instance)
        raise NotImplementedError()

    def get_projects(self, params=None):
        """
        Returns a list of ... objects
        """
        path = '/projects'
        # return self._get(path, params)._as(Project)
        raise NotImplementedError()

    def get_users(self, params=None):
        """
        Returns a list of ... objects
        """
        path = '/users'
        # return self._get(path, params)._as(User)
        raise NotImplementedError()

    def get_meters(self, params=None):
        """
        Returns a list of giraffe.service.db.Meter objects
        from a list of
            {'id': '<meter_id (int)>',
             'name': '<meter_name (string)>',
             'description': '<description>',
             'unit_name': '[seconds|..]',
             'data_type': '[float|..]'}
        dicts
        """
        path = '/meters'
        return self._get(path, params)._as(Meter)

    def get_host_meter_records(self, host, meter, params=None):
        """
        Returns a list of giraffe.service.db.MeterRecord objects
        from a list of
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
        return self._get(path, params)._as(MeterRecord)

    def get_inst_meter_records(self, inst, meter, params=None):
        """
        Returns a list of giraffe.service.db.MeterRecord objects
        from a list of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/instances', inst, 'meters', meter])
        return self._get(path, params)._as(MeterRecord)

    def get_proj_meter_records(self, host, meter, params=None):
        """
        Returns a list of giraffe.service.db.MeterRecord objects
        from a list of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/projects', host, 'meters', meter])
        # return self._get(path, params)._as(MeterRecord)
        raise NotImplementedError()

    def get_user_meter_records(self, host, meter, params=None):
        """
        Returns a list of giraffe.service.db.MeterRecord objects
        from a list of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/users', host, 'meters', meter])
        # return self._get(path, params)._as(MeterRecord)
        raise NotImplementedError()
