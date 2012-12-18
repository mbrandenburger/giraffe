import json
import logging
import threading
import re
from functools import wraps
from flask import Flask, Response, request
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

        self.app = Flask(__name__)

        def requires_auth(f):
            return self.__requires_auth(f)

        @self.app.route('/')
        def welcome():
            return self.__welcome()

        @self.app.route('/hosts')
        @self.app.route('/hosts/')
        @requires_auth
        def hosts():
            return self.__hosts()

        @self.app.route('/projects')
        @self.app.route('/projects/')
        @requires_auth
        def projects():
            return self.__projects()

        @self.app.route('/users')
        @self.app.route('/users/')
        @requires_auth
        def users():
            return self.__users()

        @self.app.route('/instances')
        @self.app.route('/instances/')
        @requires_auth
        def instances():
            return self.__instances()

        @self.app.route('/hosts/<host_id>/meters/<meter_id>')
        @self.app.route('/hosts/<host_id>/meters/<meter_id>/')
        @requires_auth
        def hosts_hid_meters_mid(host_id, meter_id):
            return self.__hosts_hid_meters_mid(host_id, meter_id)

        @self.app.route('/projects/<project_id>/meters/<meter_id>')
        @self.app.route('/projects/<project_id>/meters/<meter_id>/')
        @requires_auth
        def projects_pid_meters_mid(project_id, meter_id):
            return self.__projects_pid_meters_mid(project_id, meter_id)

        @self.app.route('/users/<user_id>/meters/<meter_id>')
        @self.app.route('/users/<user_id>/meters/<meter_id>/')
        @requires_auth
        def users_pid_meters_mid(user_id, meter_id):
            return self.__users_uid_meters_mid(user_id, meter_id)

        @self.app.route('/instances/<instance_id>/meters/<meter_id>')
        @self.app.route('/instances/<instance_id>/meters/<meter_id>/')
        @requires_auth
        def instances_iid_meters_mid(instance_id, meter_id):
            return self.__instances_iid_meters_mid(instance_id, meter_id)

        threading.Thread.__init__(self)

    def run(self):
        self.app.run(host=_config.get('flask', 'host'),
                     port=_config.getint('flask', 'port'))

    def stop(self):
        self._Thread__stop()

    def __query_params(self):
        """
        Returns the query parameters for the current request as a dictionary.
        Values of the format "YYYY-MM-DD_HH-ii-ss" are converted to the format
        "YYYY-MM-DD HH:ii:ss".
        """
        query_parts = request.query_string.split('&')
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

    def __requires_auth(self, f):
        def __check_auth(username, password):
            """
            checks whether a username/password combination is valid
            """
            return (username == _config.get('flask', 'user') and
                    password == _config.get('flask', 'pass'))

        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not (auth and __check_auth(auth.username, auth.password)):
                """
                sends a 401 response that enables basic auth
                """
                return Response({'message': 'Unauthorized'}, 401,
                                {'WWW-Authenticate':
                                 'Basic realm="REST API Login"'})
            return f(*args, **kwargs)
        return decorated

    def __welcome(self):
        return Response(response='Welcome to Giraffe REST API', status=200)

    def __hosts(self):
        """
        Route: hosts
        """
        self.db.session_open()
        hosts = self.db.load(Host)
        self.db.session_close()
        return json.dumps([host.to_dict() for host in hosts])

    def __projects(self):
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

    def __users(self):
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

    def __instances(self):
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

    def ___hosts_hid(self):
        """
        Route: hosts/<host_id>
        """
        return 'TODO'

    def __hosts_hid_meters_mid(self, host_id, meter_id):
        """
        Route: hosts/<host_id>/meters/<meter_id>
        """
        self.db.session_open()
        hosts = self.db.load(Host, {'name': host_id}, limit=1)
        if not hosts:
            return Response(response='host_name not found', status=404)
        host = hosts[0]

        meters = hosts = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'host_id': host.id, 'meter_id': meter.id}
        query_params = self.__query_params()
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

    def __projects_pid_meters_mid(self, project_id, meter_id):
        """
        Route: projects/<project_id>/meters/<meter_id>
        """
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'project_id': project_id, 'meter_id': meter.id}
        query_params = self.__query_params()
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

    def __users_uid_meters_mid(self, user_id, meter_id):
        """
        Route: users/<user_id>/meters/<meter_id>
        """
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'user_id': user_id, 'meter_id': meter.id}
        query_params = self.__query_params()
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

    def __instances_iid_meters_mid(self, instance_id, meter_id):
        """
        Route: instances/<instance_id>/meters/<meter_id>
        """
        self.db.session_open()
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        # narrow down the search
        limit = self.RESULT_LIMIT
        order = 'asc'
        search_params = {'resource_id': instance_id, 'meter_id': meter.id}
        query_params = self.__query_params()
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
