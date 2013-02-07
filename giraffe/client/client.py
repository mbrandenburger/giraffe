"""
Command-line interface to the Giraffe API.

Usage:
    Type ./start_client.sh --help or ./start_client.sh -h for help.

    ./start_client.sh <CMD> <PARAM ...> <ARG ...>

    Commands (CMD):
        meters
        hosts
        instances
        projects
        users

        host-meter
        inst-meter (alias: instance-meter)
        proj-meter (alias: project-meter)
        user-meter

    Required parameters (PARAM) [in combination with certain commands]:
        --host HOST          (required with 'host-meter')
        --instance INSTANCE  (required with 'inst-meter')
        --project PROJECT    (required with 'proj-meter')
        --user USER          (required with 'user-meter')
        --meter METER        (required in combination with all of the above)

    Additional, optional query parameters and arguments (PARAM, ARG):
        --count
        --limit LIMIT
        --order ORDER
        --start TIME
        --end   TIME

        --chart     ...
        --json      display output as plain JSON (DEFAULT)
        --csv       diplay output as CSV
        --tab       output as table

    Instead of using the CMD interface, one can also query the Giraffe API
    using a query URL (encoded as REST API URL path):
        -q QUERY, --query QUERY
    [Note: When using this parameter, query args/params - like `--count` -
           will be ignored; on the other hand, this parameter is overriden
           by giraffe-client command calls.]

    Additional configuration parameters (if not provided, information needs
    to be stored in env. variables or in Giraffe's config file, [client] 
    section.)
        -u USERNAME, --username USERNAME
        -p PASSWORD, --password PASSWORD
        --tenant_id TENANT_ID
        --tenant_name TENANT_NAME
        -e ENDPOINT, --endpoint ENDPOINT
        -a AUTH_URL, --auth_url AUTH_URL
"""

__author__  = 'fbahr, marcus'
__version__ = '0.4.0'
__date__    = '2013-02-07'


from cement.core import foundation, controller  # < cement 2.0.2
import requests                                 # < requests 0.14.2
import os
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
from giraffe.client.api import GiraffeClient
from giraffe.client.formatter import * 
from giraffe.common.config import Config
from giraffe.common.url_builder import URLBuilder
from giraffe.common.auth import AuthProxy

import logging
logger = logging.getLogger("client")


class BaseController(controller.CementBaseController):
    """
    GiraffeClient's (base) controller
    """

#   def __init__(self, *args, **kwargs):
#       super(BaseController, self).__init__(args, kwargs)


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
            (['--start'], \
                dict(action='store', help='START_TIME', \
                     default=None)),
            (['--end'], \
                dict(action='store', help='END_TIME', \
                     default=None)),
            (['--count'], \
                dict(action='store_true', help='', \
                     default=False)),
            (['--limit'], \
                dict(action='store', help='LIMIT', \
                     default=0)),
            (['--order'], \
                dict(action='store', help='ASC (default) or DESC', \
                     default=None)),
            # -----------------------------------------------------------------
            # (['--jsn'], \
            #     dict(action='store_true', help='display output as plain JSON', \
            #         default=None)),
            (['--csv'], \
                 dict(action='store_true', help='diplay output as CSV', \
                      default=None)),
            (['--tab'], \
                 dict(action='store_true', help=' output as table', \
                      default=None)),
            # -----------------------------------------------------------------
            (['-a', '--auth_url'], \
                dict(action='store', help='$OS_AUTH_URL', \
                     default=os.getenv('OS_AUTH_URL') or \
                             _config.get('client', 'auth_url'))),
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
                             _config.get('client', 'tenant_id'))),
            (['--tenant_name'], \
                dict(action='store', help='$OS_TENANT_NAME', \
                     default=os.getenv('OS_TENANT_NAME') or \
                             _config.get('client', 'tenant_name'))),
            # -----------------------------------------------------------------
            (['-e', '--endpoint'], \
                dict(action='store', help='Giraffe service endpoint (domain:port)', \
                     default=':'.join([_config.get('client', 'host'), \
                                       _config.get('client', 'port')])))
            ]
        #   ...
        #   (['-F', '--FLAG'],     dict(action='store_true', help='...'))

    # @end class Meta ---------------------------------------------------------


    def _client(self):
        _kwargs = dict((k,v) for (k,v) in self.pargs._get_kwargs())
        auth_token = AuthProxy.get_token(credentials=_kwargs)
        return GiraffeClient(auth_token)

    def _params(self):
        params = {}
        if self.pargs.count: params['aggregation'] = 'count'
        if self.pargs.start: params['start_time'] = self.pargs.start
        if self.pargs.end: params['end_time'] = self.pargs.end
        if self.pargs.limit: params['limit'] = self.pargs.limit
        if self.pargs.order: params['order'] = self.pargs.order
        return params

    def _formatter(self):
        try:
            if self.pargs.tab:
                return TabFormatter
            elif self.pargs.csv:
                return CsvFormatter
            else:
                return JsonFormatter

        except Exception as e:
            print e

    def _display(self, result):
        try:
            items = result._as(Text, formatter=self._formatter())
            print '\n', '\n'.join(items), '\n'
        except:
            print '\n', result, '\n'

    @controller.expose(hide=True)
    def default(self):
        url = None

        try:
            if not self.pargs.query:
                raise Exception('Query parameter missing.')

            url = URLBuilder.build(endpoint=self.pargs.endpoint,
                                   path=self.pargs.query)
            logger.debug('Query: %s' % url)

            #@[fbahr]: dirty hack, getting dict instance from self.pargs
            _kwargs = dict((k,v) for (k,v) in self.pargs._get_kwargs())
            auth_token = AuthProxy.get_token(credentials=_kwargs)

            r = requests.get(url, headers={'X-Auth-Token': auth_token})

            logger.debug('HTTP response status code: %s' % r.status_code)
            r.raise_for_status()

        except requests.exceptions.HTTPError:
            # @[fbahr]: What if... server down?
            print '\nBad request [HTTP %s]: %s' % (r.status_code, url)

        except:
            # @fbahr: dirty hack...
            help_text = []
            help_text.append('usage: ' + self._usage_text)
            help_text.append('Try "[start_]client.py --help" for help on a specific command.\n')
            print '\n'.join(help_text)

    @controller.expose()
    def hosts(self):
        result = self._client().get_hosts(self._params())
        self._display(result)

    @controller.expose()
    def instances(self):
        result = self._client().get_instances(self._params())
        self._display(result)

    @controller.expose()
    def projects(self):
        result = self._client().get_projects(self._params())
        self._display(result)

    @controller.expose()
    def users(self):
        result = self._client().get_users(self._params())
        self._display(result)

    @controller.expose()
    def meters(self):
        result = self._client().get_meters(self._params())
        self._display(result)

    @controller.expose()
    def host_meter(self):
        result = self._client().get_host_meter_records( \
                                    self.pargs.host, self.pargs.meter, \
                                    self._params())
        self._display(result)

    @controller.expose(aliases=['instance-meter'])
    def inst_meter(self):
        result = self._client().get_inst_meter_records( \
                                    self.pargs.instance, self.pargs.meter, \
                                    self._params())
        self._display(result)

    @controller.expose(aliases=['project-meter'])
    def proj_meter(self):
        result = self._client().get_proj_meter_records( \
                                    self.pargs.project, self.pargs.meter, \
                                    self._params())
        self._display(result)

    @controller.expose()
    def user_meter(self):
        result = self._client().get_user_meter_records( \
                                    self.pargs.user, self.pargs.meter, \
                                    self._params())
        self._display(result)


class GiraffeClientApp(foundation.CementApp):
    class Meta:
        label = 'giraffe-client'
        base_controller = BaseController()

    def __init__(self, **kwargs):
        super(GiraffeClientApp, self).__init__(kwargs)


def main():
    #creating an application
    app = GiraffeClientApp()

    try:
        # setting up the application
        app.setup()
        app.run()
    except Exception as e:
        logger.exception('%s' % e)
    finally:
        # closing the application
        app.close()


if __name__ == '__main__':
    main()
