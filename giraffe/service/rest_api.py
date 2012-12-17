__author__ = 'marcus, fbahr'

import json
import logging
import threading
from functools import wraps
from flask import Flask, Response, request
from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Host, Meter, MeterRecord


_logger = logging.getLogger("service.collector")
_config = Config("giraffe.cfg")


class Rest_API(threading.Thread):

    def __init__(self):
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
        self.db.session_open()
        self.app.run(host=_config.get('flask', 'host'),
                     port=_config.getint('flask', 'port'))

    def stop(self):
        self.db.session_close()
        self._Thread__stop()

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
                                {'WWW-Authenticate': 'Basic realm="REST API Login"'})
            return f(*args, **kwargs)
        return decorated

    def __welcome(self):
        return Response(response='Welcome to Giraffe REST API', status=200)

    def __hosts(self):
        """
        Route: hosts
        """
        return json.dumps([host.to_dict() for host in self.db.load(Host)])

    def __projects(self):
        """
        Route: projects
        """
        return Response(response='not yet implemented', status=404)

    def __users(self):
        """
        Route: users
        """
        return Response(response='not yet implemented', status=404)

    def __instances(self):
        """
        Route: instances
        """
        return Response(response='not yet implemented', status=404)

    def ___hosts_hid(self):
        """
        Route: hosts/<host_id>
        """
        return 'TODO'

    def __hosts_hid_meters_mid(self, host_id, meter_id):
        """
        Route: hosts/<host_id>/meters/<meter_id>
        """
        hosts = self.db.load(Host, {'name': host_id}, limit=1)
        if not hosts:
            return Response(response='host_name not found', status=404)
        host = hosts[0]

        meters = hosts = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        records = self.db.load(MeterRecord,
                                  {'host_id': host.id, 'meter_id': meter.id})

        return json.dumps([r.to_dict() for r in records])

    def __projects_pid_meters_mid(self, project_id, meter_id):
        """
        Route: projects/<project_id>/meters/<meter_id>
        """
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        records = self.db.load(MeterRecord, {'project_id': project_id,
                                             'meter_id': meter.id})
        return json.dumps([r.to_dict() for r in records])

    def __users_uid_meters_mid(self, user_id, meter_id):
        """
        Route: users/<user_id>/meters/<meter_id>
        """
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]

        records = self.db.load(MeterRecord, {'user_id': user_id,
                                             'meter_id': meter.id})
        return json.dumps([r.to_dict() for r in records])

    def __instances_iid_meters_mid(self, instance_id, meter_id):
        """
        Route: instances/<instance_id>/meters/<meter_id>
        """
        meters = self.db.load(Meter, {'name': meter_id}, limit=1)
        if not meters:
            return Response(response='meter_name not found', status=404)
        meter = meters[0]
        records = self.db.load(MeterRecord, {'resource_id': instance_id,
                                             'meter_id': meter.id})
        return json.dumps([r.to_dict() for r in records])
