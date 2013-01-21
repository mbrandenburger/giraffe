import json
import logging
import threading
import re
import giraffe.service.rest_server as srv
from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Host, Meter, MeterRecord


_logger = logging.getLogger("service.collector")
_config = Config("giraffe.cfg")


class Rest_API(threading.Thread):

    def __init__(self):
        self.PARAM_START_TIME = 'start_time'
        self.PARAM_END_TIME = 'end_time'
        self.PARAM_AGGREGATION = 'aggregation'
        self.PARAM_CHART = 'chart'
        self.PARAM_LATEST = 'latest'
        self.RESULT_LIMIT = 2500
        self.__pattern_timestamp = re.compile(
                '^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})$')
        self.db = db.connect('%s://%s:%s@%s/%s' % (
                                    _config.get('db', 'vendor'),
                                    _config.get('db', 'user'),
                                    _config.get('db', 'pass'),
                                    _config.get('db', 'host'),
                                    _config.get('db', 'schema')))
        self.server = None
        threading.Thread.__init__(self)

    def run(self):
        conf = dict(log_name='Auth',
            auth_host=_config.get('service', 'auth_host'),
            auth_port=_config.getint('service', 'auth_port'),
            auth_protocol=_config.get('service', 'auth_protocol'),
            admin_token=_config.get('service', 'admin_token'),
            delay_auth_decision=_config.getint('service', 'delay_auth_decision'),
            rest_api=self,
            host=_config.get('flask', 'host'),
            port=_config.getint('flask', 'port'),
            user=_config.get('flask', 'user'),
            password=_config.get('flask', 'pass'))

        self.server = srv.start(conf)
#        self.server = srv.start(self, host=_config.get('flask', 'host'),
#                                      port=_config.getint('flask', 'port'),
#                                      user=_config.get('flask', 'user'),
#                                      password=_config.get('flask', 'pass'))

    def stop(self):
        self._Thread__stop()

    def __query_params(self, query_string):
        """
        Returns the query parameters for the current request as a dictionary.
        Values of the format "YYYY-MM-DD_HH-ii-ss" are converted to the format
        "YYYY-MM-DD HH:ii:ss".
        """
        query_parts = query_string.split('&')
        params = {}
        for query_part in query_parts:
            parts = query_part.split('=', 2)
            try:
                params[parts[0]] = parts[1]
                matches = self.__pattern_timestamp.match(parts[1])
                if matches:
                    params[parts[0]] = '%s-%s-%s %s:%s:%s' % (matches.group(1),
                                                              matches.group(2),
                                                              matches.group(3),
                                                              matches.group(4),
                                                              matches.group(5),
                                                              matches.group(6))
            except Exception:
                continue
        return params

    def route_root(self):
        return 'Welcome to Giraffe REST API'

    def route_hosts(self):
        """
        Route: hosts
        """
        self.db.session_open()
        hosts = self.db.load(Host)
        self.db.session_close()
        return json.dumps([host.to_dict() for host in hosts])

    def route_projects(self):
        """
        Route: projects
        """
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, 'project_id')
        # remove null values
        if None in values:
            values.remove(None)
        self.db.session_close()
        return json.dumps(values)

    def route_users(self):
        """
        Route: users
        """
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, 'user_id')
        # remove null values
        if None in values:
            values.remove(None)
        self.db.session_close()
        return json.dumps(values)

    def route_instances(self):
        """
        Route: instances
        """
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, 'resource_id')
        # remove null values
        if None in values:
            values.remove(None)
        self.db.session_close()
        return json.dumps(values)

    def route_meters(self):
        """
        Route: meters
        """
        self.db.session_open()
        meters = self.db.load(Meter, order='asc', order_attr='name')
        self.db.session_close()
        return json.dumps([meter.to_dict() for meter in meters])

    def route_hosts_hid(self):
        """
        Route: hosts/<host_id>
        """
        return 'TODO'

    def route_hosts_hid_meters_mid(self, host_id, meter_id, query_string=''):
        """
        Route: hosts/<host_id>/meters/<meter_id>
        """
        self.db.session_open()
        hosts = self.db.load(Host, {'name': host_id}, limit=1)
        if not hosts:
            return None
        host = hosts[0]

        meters = hosts = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'host_id': host.id, 'meter_id': meter.id}
        query_params = self.__query_params(query_string)
        if self.PARAM_START_TIME in query_params or self.PARAM_END_TIME in query_params:
            search_params['timestamp'] = ['0000-01-01 00:00:00',
                                          '2999-12-31 23:59:59']
            if self.PARAM_START_TIME in query_params:
                search_params['timestamp'][0] = query_params[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query_params:
                search_params['timestamp'][1] = query_params[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query_params and query_params[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'
        records = self.db.load(MeterRecord, search_params, limit=limit, order=order)
        self.db.session_close()
        return json.dumps([r.to_dict() for r in records])

    def route_projects_pid_meters_mid(self, project_id, meter_id, query_string=''):
        """
        Route: projects/<project_id>/meters/<meter_id>
        """
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'project_id': project_id, 'meter_id': meter.id}
        query_params = self.__query_params(query_string)
        if self.PARAM_START_TIME in query_params or self.PARAM_END_TIME in query_params:
            search_params['timestamp'] = ['0000-01-01 00:00:00',
                                          '2999-12-31 23:59:59']
            if self.PARAM_START_TIME in query_params:
                search_params['timestamp'][0] = query_params[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query_params:
                search_params['timestamp'][1] = query_params[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query_params and query_params[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'
        records = self.db.load(MeterRecord, search_params, limit=limit, order=order)
        self.db.session_close()
        return json.dumps([r.to_dict() for r in records])

    def route_users_uid_meters_mid(self, user_id, meter_id, query_string=''):
        """
        Route: users/<user_id>/meters/<meter_id>
        """
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'user_id': user_id, 'meter_id': meter.id}
        query_params = self.__query_params(query_string)
        if self.PARAM_START_TIME in query_params or self.PARAM_END_TIME in query_params:
            search_params['timestamp'] = ['0000-01-01 00:00:00',
                                          '2999-12-31 23:59:59']
            if self.PARAM_START_TIME in query_params:
                search_params['timestamp'][0] = query_params[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query_params:
                search_params['timestamp'][1] = query_params[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query_params and query_params[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'
        records = self.db.load(MeterRecord, search_params, limit=limit, order=order)
        self.db.session_close()
        return json.dumps([r.to_dict() for r in records])

    def route_instances_iid_meters_mid(self, instance_id, meter_id, query_string=''):
        """
        Route: instances/<instance_id>/meters/<meter_id>
        """
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'resource_id': instance_id, 'meter_id': meter.id}
        query_params = self.__query_params(query_string)
        if self.PARAM_START_TIME in query_params or self.PARAM_END_TIME in query_params:
            search_params['timestamp'] = ['0000-01-01 00:00:00',
                                          '2999-12-31 23:59:59']
            if self.PARAM_START_TIME in query_params:
                search_params['timestamp'][0] = query_params[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query_params:
                search_params['timestamp'][1] = query_params[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query_params and query_params[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'
        records = self.db.load(MeterRecord, search_params, limit=limit, order=order)
        self.db.session_close()
        return json.dumps([r.to_dict() for r in records])
