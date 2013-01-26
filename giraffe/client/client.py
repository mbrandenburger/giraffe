"""
usage: ./start_client -r=<query>
                            ^ e.g., <query>="/hosts/<host-id>"
"""
__author__  = 'fbahr, marcus'
__version__ = '0.2.0'
__date__    = '2013-01-21'


from cement.core import foundation, controller  # < cement 2.0.2
import requests                                 # < requests 0.14.2
import json
import os
# from prettytable import PrettyTable
from datetime import datetime
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
from giraffe.common.config import Config
from giraffe.service.db import Meter, MeterRecord
from keystoneclient.v2_0 import client as ksclient

import logging
logger = logging.getLogger("client")


def _create_url_from(endpoint, path, params=None):
    url = ''.join(['http://', endpoint, path, '?' if params else ''])
    if params:
        url = url + '&'.join(params)
    return url


class BaseController(controller.CementBaseController):
    """
    GiraffeClient's (base) controller
    """

#   def __init__(self, *args, **kwargs):
#       super(BaseController, self).__init__(*args, **kwargs)


    def authAndReturnToken(self):
#       TODO(Marcus): Add CLI params
        kwargs = {
            'username': os.getenv('OS_USERNAME'),
            'password': os.getenv('OS_PASSWORD'),
            'tenant_id': os.getenv('OS_TENANT_ID'),
            'tenant_name': os.getenv('OS_TENANT_NAME'),
            'auth_url':  os.getenv('OS_AUTH_URL'),
            'service_type': os.getenv('OS_SERVICE_TYPE'),
            'endpoint_type': os.getenv('OS_ENDPOINT_TYPE'),
            'insecure': False
        }
        _ksclient = ksclient.Client(username=kwargs.get('username'),
            password=kwargs.get('password'),
            tenant_id=kwargs.get('tenant_id'),
            tenant_name=kwargs.get('tenant_name'),
            auth_url=kwargs.get('auth_url'),
            insecure=kwargs.get('insecure'))

        return _ksclient.auth_token

    class Meta:
        """
        Model that acts as a container for the controller's meta-data.
        """

        label       = 'base'
        description = 'Command-line interface to the Giraffe API.'

        _config     = Config('giraffe.cfg')


        # command line arguments
        arguments = [
            (['-a', '--auth_url'], dict(action='store', help='$OS_AUTH_URL',    default=None)),
            (['-u', '--username'], dict(action='store', help='$OS_USERNAME',    default=_config.get('client', 'user'))),
            (['-p', '--password'], dict(action='store', help='$OS_PASSWORD',    default=_config.get('client', 'pass'))),
            (['--tenant_id'],      dict(action='store', help='$OS_TENANT_ID',   default=None)),
            (['--tenant_name'],    dict(action='store', help='$OS_TENANT_NAME', default=None)),

            (['-e', '--endpoint'], dict(action='store', help='Service endpoint (domain:port)', default=':'.join([_config.get('client', 'host'), _config.get('client', 'port')]))),
            (['-r', '--request'],  dict(action='store', help='encoded as URL path',            default=None)),

            (['--json'],           dict(action='store_true', help='display output as plain JSON', default=True)),
            (['--csv'],            dict(action='store_true', help='display output as CSV',        default=False)),
            (['--tab'],            dict(action='store_true', help='display output as table',      default=False))
            ]
        #   ...
        #   (['-F', '--FLAG'],     dict(action='store_true', help='...'))
        #   ...


    @controller.expose(hide=True)
    def default(self):
        url = None

        try:
            url = ''.join(['http://', self.pargs.endpoint, self.pargs.request])
            logger.debug('Query: %s' % url)

            #r = requests.get(url, headers=auth_header)
            auth_token = self.authAndReturnToken()
            auth_header = {'X-Auth-Token': auth_token}

#           TODO(Marcus): Auth is depricated ... remove
            r = requests.get(url, auth=(self.pargs.username,
                                        self.pargs.password),
                            headers=auth_header)

            logger.debug('HTTP response status code: %s' % r.status_code)

            r.raise_for_status()

            if self.pargs.csv:
                self.__print_as_csv(r.json)
            elif self.pargs.tab:
                self.__print_as_tab(r.json)
            else:
                print json.dumps(r.json, indent=4)

        except requests.exceptions.HTTPError:
            print '\nBad request [HTTP %s]: %s' % (r.status_code, url)

        except:
            # @fbahr: dirty hack...
            help_text = [] 
            help_text.append('usage: ' + self._usage_text)
            help_text.append('\nSee "client.py --help" for help on a specific command.')
            print '\n'.join(help_text)


    def __print_as_csv(self, r_json):
        if not r_json:
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
                    dt    = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                    # @fbahr: dirty hack
                    # d_ord = dt.toordinal() * 24 * 3600
                    # t_ord = dt.hour * 3600 + dt.minute * 60 + dt.second
                    # val   = d_ord + t_ord
                    delta = UNIX_EPOCH - dt
                    val   = - delta.days * 24 * 3600 + delta.seconds
                row.append(str(val))
            print '\t'.join(row)


    def __print_as_tab(self, r_json):
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
        self.endpoint = ':'.join([self.config.get('client', 'host'),
                                  self.config.get('client', 'port')])

    def meters(self, query_params=None):
        request = '/meters'
        url = ''.join(['http://', self.endpoint, request])
        lst = requests.get(url, auth=(self.username, self.password)).json
        # ^ lst = list of
        #           {u'unit_name': u'[seconds|..]',
        #            u'description': u'<description>',
        #            u'id': u'<meter_id (int)>',
        #            u'data_type': u'[float|..]',
        #            u'name': u'<meter_name (string)>'}
        #         dicts
        meters = []
        for elem in lst:
            m = Meter()
            m.id = elem['id']
            m.name = elem['name']
            m.description = elem['description']
            m.unit_name = elem['unit_name']
            m.data_type = elem['data_type']
            meters.append(m)
        return meters


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
