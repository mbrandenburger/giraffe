__author__ = 'marcus, fbahr'

import json
import logging
import threading
from functools import wraps
from flask import Flask, Response, request
from giraffe.common.config import Config
import giraffe.service.db as db
from giraffe.service.db import Meter, MeterRecord


_logger = logging.getLogger("service.collector")
_config = Config("giraffe.cfg")


class Rest_API(threading.Thread):

    def __init__(self):
        self.appdb = db.connect('%s://%s:%s@%s/%s' % (
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

        @self.app.route('/hosts/<host_id>/meters/<meter_id>')
        @self.app.route('/hosts/<host_id>/meters/<meter_id>/')
        @requires_auth
        def host_meter(host_id, meter_id):
            return self.__host_meter(host_id, meter_id)

        threading.Thread.__init__(self)

    def run(self):
        self.appdb.session_open()
        self.app.run(_config.get('flask', 'host'), _config.getint('flask', 'port'))
        # e.g., host='134.169.176.116'      , port=1337

    def stop(self):
        self.appdb.session_close()
        self._Thread__stop()

    def __requires_auth(self, f):
        def __check_auth(username, password):
            """
            checks whether a username/password combination is valid
            """
            return ( username == _config.get('flask', 'user') and
                     password == _config.get('flask', 'pass') )

        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not (auth and __check_auth(auth.username, auth.password)):
                """
                sends a 401 response that enables basic auth
                """
                return Response({ 'message' : 'Could not verify your access'
                                              ' level for this URL. You have' 
                                              ' to login with proper'
                                              ' credentials.' },
                                401,
                                {'WWW-Authenticate': 'Basic realm="Login Required"'})
            return f(*args, **kwargs)
        return decorated

    def __welcome(self):
        return json.dumps({ 'message' : 'Welcome to Giraffe REST API' })

    def __hosts(self):
        return json.dumps({ 'message' : '<List of all hosts>' })

    def __host_meter(self, host_id, meter_id):
        # ?
        meter   = self.appdb.load(Meter,
                                  {'id' : meter_id},
                                  limit=1)[0]
        records = self.appdb.load(MeterRecord,
                                  {'host_id' : host_id, 'meter_id' : meter_id},
                                  limit=None)

        # print { 'meter' : meter, 'records'  : records }
        print json.dumps({ 'meter' : meter, 'records'  : records })
        return json.dumps({ 'meter' : meter, 'records'  : records})

        # message = {}
        # message['host']       = host_id
        # message['meter']      = meter_id
        # message['start_time'] = start_time
        #
        # return json.dumps(message)
