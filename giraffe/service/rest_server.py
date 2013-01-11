import logging
from functools import wraps
from flask import Flask, Response, request

logger = logging.getLogger("service.rest_server")


def start(rest_api, host, port, user=None, password=None):
    return Rest_Server(rest_api=rest_api,
                       host=host,
                       port=port,
                       username=user,
                       password=password)


class Rest_Server():
    def __init__(self, rest_api, host, port, username, password):
        self.app = Flask(__name__)
        self.app.config['PROPAGATE_EXCEPTIONS'] = True
        self.rest_api = rest_api
        self.username = username
        self.password = password
        self.request = None

        def requires_auth(f):
            return self.__requires_auth(f)

        @self.app.route('/')
        def root():
            logger.debug('in the root route!')
            result = self.rest_api.route_root()
            if result is None:
                return Response(response='root not available', status=404)
            return Response(response=result, status=200)

        @self.app.route('/hosts')
        @self.app.route('/hosts/')
        @requires_auth
        def hosts():
            result = self.rest_api.route_hosts()
            if result is None:
                return Response(response='hosts not available', status=404)
            return self.rest_api.route_hosts()

        @self.app.route('/projects')
        @self.app.route('/projects/')
        @requires_auth
        def projects():
            result = self.rest_api.route_projects()
            if result is None:
                return Response(response='projects not available', status=404)
            return result

        @self.app.route('/users')
        @self.app.route('/users/')
        @requires_auth
        def users():
            result = self.rest_api.route_users()
            if result is None:
                return Response(response='users not available', status=404)
            return result

        @self.app.route('/instances')
        @self.app.route('/instances/')
        @requires_auth
        def instances():
            logger.debug('aetschibaetschi')
            result = self.rest_api.route_instances()
            if result is None:
                return Response(response='instances not available', status=404)
            return result

        @self.app.route('/meters')
        @self.app.route('/meters/')
        @requires_auth
        def meters():
            result = self.rest_api.route_meters()
            if result is None:
                return Response(response='meters not available', status=404)
            return result

        @self.app.route('/hosts/<host_id>/meters/<meter_id>')
        @self.app.route('/hosts/<host_id>/meters/<meter_id>/')
        @requires_auth
        def hosts_hid_meters_mid(host_id, meter_id):
            result = self.rest_api.route_hosts_hid_meters_mid(host_id,
                                                              meter_id,
                                                              request.query_string)
            if result is None:
                return Response(response='host or meter not available', status=404)
            return result

        @self.app.route('/projects/<project_id>/meters/<meter_id>')
        @self.app.route('/projects/<project_id>/meters/<meter_id>/')
        @requires_auth
        def projects_pid_meters_mid(project_id, meter_id):
            result = self.rest_api.route_projects_pid_meters_mid(project_id,
                                                                 meter_id,
                                                                 request.query_string)
            if result is None:
                return Response(response='project or meter not available', status=404)
            return result

        @self.app.route('/users/<user_id>/meters/<meter_id>')
        @self.app.route('/users/<user_id>/meters/<meter_id>/')
        @requires_auth
        def users_pid_meters_mid(user_id, meter_id):
            result = self.rest_api.route_users_uid_meters_mid(user_id,
                                                              meter_id,
                                                              request.query_string)
            if result is None:
                return Response(response='user or meter not available', status=404)
            return result

        @self.app.route('/instances/<instance_id>/meters/<meter_id>')
        @self.app.route('/instances/<instance_id>/meters/<meter_id>/')
        @requires_auth
        def instances_iid_meters_mid(instance_id, meter_id):
            result = self.rest_api.route_instances_iid_meters_mid(instance_id,
                                                                  meter_id,
                                                                  request.query_string)
            if result is None:
                return Response(response='instance or meter not available', status=404)
            return result

        # this line starts the flask server
        self.app.run(host=host, port=port)

    def __requires_auth(self, f):
        def __check_auth(username, password):
            """
            checks whether a username/password combination is valid
            """
            return (username == self.username and
                    password == self.password)

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
