__author__ = 'fbahr'

import requests  # < requests 0.14.2

from giraffe.common.config import Config
from giraffe.common.url_builder import URLBuilder
from giraffe.common.auth import AuthProxy
from giraffe.service.db import Host, Meter, MeterRecord


class GiraffeClient(object):

    def __init__(self, **kwargs):
        #@[fbahr]: Hack, for the time being -----------------------------------
        self.config = Config('giraffe.cfg')
        self.auth_url = self.config.get('identity', 'auth_url')
        self.username = self.config.get('identity', 'user')
        self.password = self.config.get('identity', 'pass')
        self.tenant_name = self.config.get('identity', 'tenant_name')
        self.tenant_id = self.config.get('identity', 'tenant_id')
        # ---------------------------------------------------------------------
        self.protocol = 'http'
        self.endpoint = ':'.join([self.config.get('client', 'host'),
                                  self.config.get('client', 'port')])

    def _get(self, path, params=None):
        # ---------------------------------------------------------------------
        class _ResultSet(object):
            def __init__(self, records):
                self._records = records

            @staticmethod
            def __deserialize(cls, record):
                obj = cls()
                if cls is Host:
                    obj.__dict__.update(
                        dict((k, v)
                             for (k, v) in record.iteritems() \
                             if k in ['id', 'name']))
                elif cls is Meter:
                    obj.__dict__.update(
                        dict((k, v)
                            for (k, v) in record.iteritems() \
                            if k in ['id', 'name', 'description', \
                                     'unit_name', 'data_type']))
                elif cls is MeterRecord:
                    obj.id, obj.host_id, obj.resource_id, \
                    obj.project_id, obj.user_id, obj.meter_id, \
                    obj.timestamp, obj.value, obj.duration = \
                        record['id'], record['host_id'], \
                        record['resource_id'], record['project_id'], \
                        record['user_id'], int(record['meter_id']), \
                        record['timestamp'], record['value'], \
                        record['duration']
                return obj

            def _as(self, cls):
                return [self.__deserialize(cls, elem) for elem in self._records]
        # end of class _ResultSet ---------------------------------------------

        url = URLBuilder.build(self.protocol, self.endpoint, path, params)

        #@[marcus,fbahr]: To be moved to GiraffeClient.__init__? --------------
        auth_token = AuthProxy.get_token(
                        auth_url=self.auth_url,
                        username=self.username,
                        password=self.password,
                        tenant_name=self.tenant_name)
        # ---------------------------------------------------------------------

        lst = requests.get(url, headers={'X-Auth-Token': auth_token}).json
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
        # ...
        raise NotImplementedError()

    def get_projects(self, params=None):
        """
        Returns a list of ... objects
        """
        path = '/projects'
        # ...
        raise NotImplementedError()

    def get_users(self, params=None):
        """
        Returns a list of ... objects
        """
        path = '/users'
        # ...
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
        # ...
        raise NotImplementedError()

    def get_user_meter_records(self, host, meter, params=None):
        """
        Returns a list of giraffe.service.db.MeterRecord objects
        from a list of
            { see GiraffeClient::get_host_meter_records }
        dicts
        """
        path = '/'.join(['/users', host, 'meters', meter])
        # ...
        raise NotImplementedError()
