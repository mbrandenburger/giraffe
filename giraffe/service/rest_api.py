import json
import logging
import threading
import re
import giraffe.service.rest_server as srv
from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Host, Meter, MeterRecord
from giraffe.service.db import MIN_TIMESTAMP, MAX_TIMESTAMP


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
            delay_auth_decision=_config.getint('service',
                                               'delay_auth_decision'),
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

    def _query_params(self, query_string):
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

    def _aggregate(self, cls, aggregation, record_args):
        """
        Returns an aggregation of an attribute of the given object class
        according to the 'aggregation' parameter:
        - count: returns the number of MeterRecord objects that match the given
        arguments
        """
        if aggregation == 'count':
            return self.db.count(cls, record_args)
        return None

    def route_root(self):
        """
        Route: /
        Returns: Welcome message (string)
        Query params: -
        """
        return 'Welcome to Giraffe REST API'

    def route_hosts(self, query_string=''):
        """
        Route: hosts
        Returns: List of Host objects, JSON-formatted
        Query params: aggregation=[count]
        """
        query = self._query_params(query_string)
        _logger.debug(query)
        self.db.session_open()
        if self.PARAM_AGGREGATION in query:
            result = self._aggregate(Host, query[self.PARAM_AGGREGATION], {})
            result = json.dumps(result)
        else:
            hosts = self.db.load(Host, order='asc', order_attr='name')
            result = json.dumps([host.to_dict() for host in hosts])
        self.db.session_close()
        return result

    def route_projects(self, query_string=''):
        """
        Route: projects
        Returns: List of project names (string), JSON-formatted
        Query params: aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, column='project_id',
                                         order='asc')
        self.db.session_close()

        # remove null values
        if None in values:
            values.remove(None)

        # do count aggregation
        # note: this is a work-around until Project objects are available
        if self.PARAM_AGGREGATION in query:
            if query[self.PARAM_AGGREGATION] == 'count':
                return json.dumps(str(len(values)))
        return json.dumps(values)

    def route_users(self, query_string=''):
        """
        Route: users
        Returns: List of user names (string), JSON-formatted
        Query params: aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, column='user_id',
                                         order='asc')
        self.db.session_close()

        # remove null values
        if None in values:
            values.remove(None)

        # do count aggregation
        # note: this is a work-around until User objects are available
        if self.PARAM_AGGREGATION in query:
            if query[self.PARAM_AGGREGATION] == 'count':
                return json.dumps(str(len(values)))
        return json.dumps(values)

    def route_instances(self, query_string=''):
        """
        Route: instances
        Returns: List of instance names (string), JSON-formatted
        Query params: aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        values = self.db.distinct_values(MeterRecord, column='resource_id',
                                         order='asc')
        self.db.session_close()

        # remove null values
        if None in values:
            values.remove(None)

        # do count aggregation
        # note: this is a work-around until Instance objects are available
        if self.PARAM_AGGREGATION in query:
            if query[self.PARAM_AGGREGATION] == 'count':
                return json.dumps(str(len(values)))
        return json.dumps(values)

    def route_meters(self, query_string=''):
        """
        Route: meters
        Returns: List of Meter objects, JSON-formatted
        Query params: aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        if self.PARAM_AGGREGATION in query:
            result = self._aggregate(Meter, query[self.PARAM_AGGREGATION], {})
            result = json.dumps(result)
        else:
            meters = self.db.load(Meter, order='asc', order_attr='name')
            result = json.dumps([meter.to_dict() for meter in meters])
        self.db.session_close()
        return str(result)

    def route_hosts_hid(self):
        """
        Route: hosts/<host_id>
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: -
        """
        raise NotImplementedError(
                  "The route \"hosts/<host_id>\" is not implemented yet")

    def route_hosts_hid_meters_mid(self, host_id,
                                         meter_id,
                                         query_string=''):
        """
        Route: hosts/<host_id>/meters/<meter_id>
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        hosts = self.db.load(Host, {'name': host_id}, limit=1)
        if not hosts:
            return None
        host = hosts[0]

        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the args
        limit = self.RESULT_LIMIT
        order = 'asc'
        args = {'host_id': host.id, 'meter_id': meter.id}
        if self.PARAM_START_TIME in query or self.PARAM_END_TIME in query:
            args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
            if self.PARAM_START_TIME in query:
                args['timestamp'][0] = query[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query:
                args['timestamp'][1] = query[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query and query[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'

        if self.PARAM_AGGREGATION in query:
            result = self._aggregate(MeterRecord,
                                     query[self.PARAM_AGGREGATION],
                                     args)
            result = json.dumps(result)
        else:
            records = self.db.load(MeterRecord, args, limit=limit, order=order,
                                   order_attr='timestamp')
            result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result

    def route_projects_pid_meters_mid(self, project_id,
                                            meter_id,
                                            query_string=''):
        """
        Route: projects/<project_id>/meters/<meter_id>
        Returns: List of MeterRecord objects, JSON-formatted
        """
        query = self._query_params(query_string)
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the args
        limit = self.RESULT_LIMIT
        order = 'asc'
        args = {'project_id': project_id, 'meter_id': meter.id}
        if self.PARAM_START_TIME in query or self.PARAM_END_TIME in query:
            args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
            if self.PARAM_START_TIME in query:
                args['timestamp'][0] = query[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query:
                args['timestamp'][1] = query[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query and query[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'

        if self.PARAM_AGGREGATION in query:
            result = self._aggregate(MeterRecord,
                                     query[self.PARAM_AGGREGATION],
                                     args)
            result = json.dumps(result)
        else:
            records = self.db.load(MeterRecord, args, limit=limit, order=order,
                                   order_attr='timestamp')
            result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result

    def route_users_uid_meters_mid(self, user_id,
                                         meter_id,
                                         query_string=''):
        """
        Route: users/<user_id>/meters/<meter_id>
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the args
        limit = self.RESULT_LIMIT
        order = 'asc'
        args = {'user_id': user_id, 'meter_id': meter.id}
        if self.PARAM_START_TIME in query or self.PARAM_END_TIME in query:
            args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
            if self.PARAM_START_TIME in query:
                args['timestamp'][0] = query[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query:
                args['timestamp'][1] = query[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query and query[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'

        if self.PARAM_AGGREGATION in query:
            result = self._aggregate(MeterRecord,
                                     query[self.PARAM_AGGREGATION],
                                     args)
            result = json.dumps(result)
        else:
            records = self.db.load(MeterRecord, args, limit=limit, order=order,
                                   order_attr='timestamp')
            result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result

    def route_instances_iid_meters_mid(self, instance_id,
                                             meter_id,
                                             query_string=''):
        """
        Route: instances/<instance_id>/meters/<meter_id>
        Returns: List of MeterRecord objects, JSON-formatted
        Query params: start_time, end_time, aggregation=[count]
        """
        query = self._query_params(query_string)
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return None
        meter = meters[0]

        # narrow down the args
        limit = self.RESULT_LIMIT
        order = 'asc'
        args = {'resource_id': instance_id, 'meter_id': meter.id}
        if self.PARAM_START_TIME in query or self.PARAM_END_TIME in query:
            args['timestamp'] = [MIN_TIMESTAMP, MAX_TIMESTAMP]
            if self.PARAM_START_TIME in query:
                args['timestamp'][0] = query[self.PARAM_START_TIME]
            if self.PARAM_END_TIME in query:
                args['timestamp'][1] = query[self.PARAM_END_TIME]
        if self.PARAM_LATEST in query and query[self.PARAM_LATEST] == '1':
            limit = 1
            order = 'desc'

        if self.PARAM_AGGREGATION in query:
            result = self._aggregate(MeterRecord,
                                     query[self.PARAM_AGGREGATION],
                                     args)
            result = json.dumps(result)
        else:
            records = self.db.load(MeterRecord, args, limit=limit, order=order,
                                   order_attr='timestamp')
            result = json.dumps([r.to_dict() for r in records])
        self.db.session_close()
        return result
