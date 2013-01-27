"""
usage: ./start_client -q=<query> ...
                         ^ e.g., <query>="/hosts/<host-id>"
"""

__author__  = 'fbahr, marcus'
__version__ = '0.2.0'
__date__    = '2013-01-21'


from cement.core import foundation, controller  # < cement 2.0.2
import requests                                 # < requests 0.14.2
import json
import os
from datetime import datetime
# from prettytable import PrettyTable
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
from giraffe.common.config import Config
from giraffe.service.db import Host, Meter, MeterRecord
from keystoneclient.v2_0 import client as ksclient

import logging
logger = logging.getLogger("client")


class URLBuilder(object):
    @staticmethod
    def build(protocol, endpoint, path, params=None):
        """
        Aux function to build a URL (string) from protocol, endpoint, path,
        and parameters.
        """
        url = ''.join([protocol, '://', endpoint, path, '?' if params else ''])
        if params:
            url = url + '&'.join(params)
        return url


class AuthClient(object):
    @staticmethod
    def get_token(**kwargs):
        params = {}
        params.update(kwargs)
        # params['username'] = kwargs['username']  # os.getenv('OS_USERNAME')
        # params['password'] = kwargs['password']  # os.getenv('OS_PASSWORD')
        # params['tenant_id'] = kwargs['tenant_id']  # os.getenv('OS_TENANT_ID'),
        # params['tenant_name'] = kwargs['tenant_name']  # os.getenv('OS_TENANT_NAME')
        # params['auth_url'] = params['auth_url']  # os.getenv('OS_AUTH_URL')
        # params['service_type'] = params['service_type']  # os.getenv('OS_SERVICE_TYPE')
        # params['endpoint_type'] = params['endpoint_type']  # os.getenv('OS_ENDPOINT_TYPE')
        params['insecure'] = False

        _ksclient = ksclient.Client(
            username=params.get('username'),
            password=params.get('password'),
            tenant_id=params.get('tenant_id'),
            tenant_name=params.get('tenant_name'),
            auth_url=params.get('auth_url'),
            insecure=params.get('insecure')
        )

        return _ksclient.auth_token


class BaseController(controller.CementBaseController):
    """
    GiraffeClient's (base) controller
    """

#   def __init__(self, *args, **kwargs):
#       super(BaseController, self).__init__(*args, **kwargs)

    class Meta:
        """
        Model that acts as a container for the controller's meta-data.
        """

        label       = 'base'
        description = 'Command-line interface to the Giraffe API.'

        _config     = Config('giraffe.cfg')

        # command line arguments
        # ! Warning: os.getenv over config.get, i.e., environment variables
        #            override params defined in giraffe.cfg 
        arguments = [
            # -----------------------------------------------------------------
            (['--host'], \
                dict(action='store', help='', \
                     default=None)),
            (['--instance'], \
                dict(action='store', help='', \
                     default=None)),
            (['--project'], \
                dict(action='store', help='', \
                     default=None)),
            (['--user'], \
                dict(action='store', help='', \
                     default=None)),
            (['--meter'], \
                dict(action='store', help='', \
                     default=None)),
            # -----------------------------------------------------------------
            (['-q', '--query'], \
                dict(action='store', help='..encoded as REST API URL path '
                                          '(overriden by giraffe-client'
                                          ' method calls)', \
                     default=None)),
            # -----------------------------------------------------------------
            (['--count'], \
                dict(action='store_true', help='', \
                     default=False)),
            (['--latest'], \
                dict(action='store_true', help='', \
                     default=False)),
            # -----------------------------------------------------------------
            (['--json'], \
                 dict(action='store_true', help='display output as plain JSON', \
                      default=True)),
            (['--csv'], \
                 dict(action='store_true', help='diplay output as CSV', \
                      default=False)),
            (['--tab'], \
                 dict(action='store_true', help=' output as table', \
                      default=False)),
            # -----------------------------------------------------------------
            (['-a', '--auth_url'], \
                dict(action='store', help='$OS_AUTH_URL', \
                     default=os.getenv('OS_AUTH_URL') or \
                             _config.get('identity', 'auth_url'))),
            # -----------------------------------------------------------------
            (['-u', '--username'], \
                dict(action='store', help='$OS_USERNAME', \
                     default=os.getenv('OS_USERNAME') or \
                             _config.get('client', 'user'))),
            (['-p', '--password'], \
                dict(action='store', help='$OS_PASSWORD', \
                     default=os.getenv('OS_PASSWORD') or \
                             _config.get('client', 'pass'))),
            (['--tenant_id'], \
                dict(action='store', help='$OS_TENANT_ID', \
                     default=os.getenv('OS_TENANT_ID') or \
                             _config.get('client', 'tentant_id'))),
            (['--tenant_name'], \
                dict(action='store', help='$OS_TENANT_NAME', \
                     default=os.getenv('OS_TENANT_name') or \
                             _config.get('client', 'tentant_name'))),
            # -----------------------------------------------------------------
            (['-e', '--endpoint'], \
                dict(action='store', help='Giraffe service endpoint (domain:port)', \
                     default=':'.join([_config.get('client', 'host'), \
                                       _config.get('client', 'port')])))
            ]
        #   ...
        #   (['-F', '--FLAG'],     dict(action='store_true', help='...'))
        #   ...

    @controller.expose(hide=True)
    def default(self):
        url = None

        try:
            url = ''.join(['http://', self.pargs.endpoint, self.pargs.query])
            logger.debug('Query: %s' % url)

            # TODO(Marcus): Auth is depricated ... remove
            # auth_token = AuthClient.get_token()
            # auth_header = {'X-Auth-Token': auth_token}
            # r = requests.get(url, headers=auth_header)
            r = requests.get(url, auth=('admin', 'giraffe'))

            logger.debug('HTTP response status code: %s' % r.status_code)

            r.raise_for_status()

            if self.pargs.csv:
                self._print_as_csv(r.json)
            elif self.pargs.tab:
                self._print_as_tab(r.json)
            else:
                print json.dumps(r.json, indent=4)

        except requests.exceptions.HTTPError:
            # @[fbahr]: What if... server down?
            print '\nBad request [HTTP %s]: %s' % (r.status_code, url)

        except:
            # @fbahr: dirty hack...
            help_text = []
            help_text.append('usage: ' + self._usage_text)
            help_text.append('\nSee "client.py --help" for help on a specific command.')
            print '\n'.join(help_text)

    @controller.expose()
    def hosts(self):
        self.pargs.query = '/hosts'
        self.default()

    @controller.expose()
    def instances(self):
        self.pargs.query = '/instances'
        self.default()

    @controller.expose()
    def projects(self):
        self.pargs.query = '/projects'
        self.default()

    @controller.expose()
    def users(self):
        self.pargs.query = '/users'
        self.default()

    @controller.expose()
    def meters(self):
        self.pargs.query = '/meters'
        self.default()

    @controller.expose()
    def host_meter(self):
        self.pargs.query = '/'.join(['/hosts', \
                                     self.pargs.host \
                                        if self.pargs.host
                                        else '', \
                                     'meters', \
                                     self.pargs.meter \
                                        if self.pargs.meter
                                        else ''
                                    ])
        self.default()

    @controller.expose(aliases=['instance-meter'])
    def inst_meter(self):
        self.pargs.query = '/'.join(['/instances', \
                                     self.pargs.instance \
                                        if self.pargs.instance
                                        else '', \
                                     'meters', \
                                     self.pargs.meter \
                                        if self.pargs.meter
                                        else ''
                                    ])
        self.default()

    @controller.expose(aliases=['project-meter'])
    def proj_meter(self):
        self.pargs.query = '/'.join(['/projects', \
                                     self.pargs.project \
                                        if self.pargs.project
                                        else '', \
                                     'meters', \
                                     self.pargs.meter \
                                        if self.pargs.meter
                                        else ''
                                    ])
        self.default()

    @controller.expose()
    def user_meter(self):
        self.pargs.query = '/'.join(['/users', \
                                     self.pargs.user \
                                        if self.pargs.user
                                        else '', \
                                     'meters', \
                                     self.pargs.meter \
                                        if self.pargs.meter
                                        else ''
                                    ])
        self.default()

    def _print_as_csv(self, r_json):
        if not r_json:
            # logger.debug('Empty result set.')
            print 'Empty result set.'
            return

        row = []
        for key, val in r_json[0].iteritems():
            row.append(key)
        print '\t'.join(row)

        UNIX_EPOCH = datetime(1970, 1, 1, 0, 0)
        for msg in r_json:
            row = []
            for key, val in msg.iteritems():
                if key == 'timestamp':
                    dt = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                    # @fbahr: dirty hack
                    # d_ord = dt.toordinal() * 24 * 3600
                    # t_ord = dt.hour * 3600 + dt.minute * 60 + dt.second
                    # val   = d_ord + t_ord
                    delta = UNIX_EPOCH - dt
                    val   = - delta.days * 24 * 3600 + delta.seconds
                row.append(str(val))
            print '\t'.join(row)

    def _print_as_tab(self, r_json):
        raise NotImplementedError("Warning: not yet implemented.")


class GiraffeClient(foundation.CementApp):
    class Meta:
        label = 'giraffe-client'
        base_controller = BaseController()

    def __init__(self, **kwargs):
        super(GiraffeClient, self).__init__(kwargs)

        self.config = Config('giraffe.cfg')
        self.username = self.config.get('client', 'user')
        self.password = self.config.get('client', 'pass')
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
                    obj.__dict__.update(dict((k, v) \
                                             for (k, v) in record.iteritems() \
                                             if k in ['id', 'name']))
                    # obj.id, obj.name = \
                    #     record['id'], record['name']
                elif cls is Meter:
                    obj.__dict__.update(dict((k, v) \
                                             for (k, v) in record.iteritems() \
                                             if k in ['id', 'name', 'description', \
                                                      'unit_name', 'data_type']))
                    # obj.id, obj.name, obj.description, \
                    # obj.unit_name, obj.data_type = \
                    #     record['id'], record['name'], record['description'], \
                    #     record['unit_name'], record['data_type']
                elif cls is MeterRecord:
                    obj.id, obj.host_id, obj.resource_id, \
                    obj.project_id, obj.user_id, obj.meter_id, \
                    obj.timestamp, obj.value, obj.duration = \
                        record['id'], record['host_id'], record['resource_id'], \
                        record['project_id'], record['user_id'], int(record['meter_id']), \
                        record['timestamp'], record['value'], record['duration']
                return obj

            def _as(self, cls):
                return [self.__deserialize(cls, elem) for elem in self._records]
        # end of class _ResultSet ---------------------------------------------

        url = URLBuilder.build(self.protocol, self.endpoint, path, params)
        lst = requests.get(url, auth=(self.username, self.password)).json
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


def main():
    #creating an application
    app = GiraffeClient()

    try:
        # setting up the application
        app.setup()
        app.run()
    except Exception as e:
        print e
    finally:
        # closing the application
        app.close()


if __name__ == '__main__':
    main()
