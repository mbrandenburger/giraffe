import logging
import keystone.middleware.auth_token as auth_token
from flask import Flask, Response, request

logger = logging.getLogger('service.rest_server')


class Rest_Server():

    def start(self):
        self.app.run(self.host, self.port)

    def __init__(self, conf):
        self.app = Flask(__name__)
        self.app.config['PROPAGATE_EXCEPTIONS'] = True
        self.rest_api = conf.get('rest_api')
        self.host = conf.get('host')
        self.port = conf.get('port')

        self.request = None
        self.app.wsgi_app = auth_token.AuthProtocol(self.app.wsgi_app, conf)

        @self.app.route('/')
        def root():
            result = self.rest_api.route_root()
            if result is None:
                return Response(response='root not found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/hosts')
        @self.app.route('/hosts/')
        #requires_auth
        def hosts():
            result = self.rest_api.route_hosts(request.query_string)
            if result is None:
                return Response(response='no hosts found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/hosts/<host_id>')
        @self.app.route('/hosts/<host_id>/')
        #requires_auth
        def hosts_hid(host_id):
            result = self.rest_api.route_hosts_hid(host_id,
                                                   request.query_string)
            if result is None:
                return Response(response='host not found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/hosts/<host_id>/meters')
        @self.app.route('/hosts/<host_id>/meters/')
        #requires_auth
        def hosts_hid_meters(host_id):
            result = self.rest_api.route_hosts_hid_meters(host_id,
                                                          request.query_string)
            if result is None:
                return Response(response='no meters found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/hosts/<host_id>/meters/<meter_id>/records')
        @self.app.route('/hosts/<host_id>/meters/<meter_id>/records/')
        def hosts_hid_meters_mid_records(host_id, meter_id):
            result = self.rest_api.route_hosts_hid_meters_mid_records(\
                                       host_id, meter_id, request.query_string)
            if result is None:
                return Response(response='no records found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/projects')
        @self.app.route('/projects/')
        #requires_auth
        def projects():
            result = self.rest_api.route_projects(request.query_string)
            if result is None:
                return Response(response='no projects found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/projects/<project_id>')
        @self.app.route('/projects/<project_id>/')
        #requires_auth
        def projects_pid(project_id):
            result = self.rest_api.route_projects_pid(project_id,
                                                      request.query_string)
            if result is None:
                return Response(response='project not found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/projects/<project_id>/meters')
        @self.app.route('/projects/<project_id>/meters/')
        #requires_auth
        def projects_pid_meters(project_id):
            result = self.rest_api.route_projects_pid_meters(project_id,\
                                                         request.query_string)
            if result is None:
                return Response(response='no meters found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/projects/<project_id>/meters/<meter_id>/records')
        @self.app.route('/projects/<project_id>/meters/<meter_id>/records/')
        #requires_auth
        def projects_pid_meters_mid_records(project_id, meter_id):
            result = self.rest_api.\
                        route_projects_pid_meters_mid_records(project_id,
                                                              meter_id,\
                                                          request.query_string)
            if result is None:
                return Response(response='no records found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/meters')
        @self.app.route('/meters/')
        #requires_auth
        def meters():
            result = self.rest_api.route_meters(request.query_string)
            if result is None:
                return Response(response='no meters found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/meters/<meter_id>')
        @self.app.route('/meters/<meter_id>/')
        #requires_auth
        def meters_mid(meter_id):
            result = self.rest_api.route_meters_mid(meter_id,
                                                    request.query_string)
            if result is None:
                return Response(response='meter not found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/users')
        @self.app.route('/users/')
        #requires_auth
        def users():
            result = self.rest_api.route_users(request.query_string)
            if result is None:
                return Response(response='no users found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/users/<user_id>/meters/<meter_id>/records')
        @self.app.route('/users/<user_id>/meters/<meter_id>/records/')
        #requires_auth
        def users_pid_meters_mid_records(user_id, meter_id):
            result = self.rest_api.\
                        route_users_uid_meters_mid_records(user_id, meter_id,\
                                                       request.query_string)
            if result is None:
                return Response(response='no records found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/instances')
        @self.app.route('/instances/')
        #requires_auth
        def instances():
            result = self.rest_api.route_instances(request.query_string)
            if result is None:
                return Response(response='no instances found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/instances/<instance_id>/meters/<meter_id>/records')
        @self.app.route('/instances/<instance_id>/meters/<meter_id>/records/')
        #requires_auth
        def instances_iid_meters_mid_records(instance_id, meter_id):
            result = self.rest_api.\
                        route_instances_iid_meters_mid_records(instance_id,
                                                               meter_id,\
                                                       request.query_string)
            if result is None:
                return Response(response='no records found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/records')
        @self.app.route('/records/')
        #requires_auth
        def records():
            result = self.rest_api.route_records(request.query_string)
            if result is None:
                return Response(response='no records found', status=404)
            return Response(response=result, status=200)

        @self.app.route('/records/<record_id>')
        @self.app.route('/records/<record_id>/')
        #requires_auth
        def records_rid(record_id):
            result = self.rest_api.route_records_rid(record_id,
                                                     request.query_string)
            if result is None:
                return Response(response='record not found', status=404)
            return Response(response=result, status=200)
