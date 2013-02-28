__author__ = 'fbahr'

"""
Command-line interface to the Giraffe REST API.

Usage:
    ./start_client.sh <CMD> [--arguments] [--options]

    Commands:
        hosts     (alias: host)
        projects  (alias: proj)
        users     (alias: user)
        instances (alias: inst)

        meters
        records

    Furthermore, there's - for debugging purposed only - a hidden 'query'
    command to query the Giraffe API directly using a REST API path.

    Required arguments [in combination with certain commands]:
        **TO BE DONE**

    Additional, optional command options and arguments:
        --count
        --start TIME
        --end   TIME
        --min
        --max
        --avg
        --hourly
        --daily
      [ --first-last : NOT_IMPLEMENTED! ]
        --sum
        --limit LIMIT
        --order ORDER  (ASC [default] or DESC)

      [ --jsn       output as plain JSON ] **REMOVED** (but still: DEFAULT)
        --csv       output as CSV
        --tab       output as table
      [ --chart     : NOT_IMPLEMENTED! ]

    Additional configuration parameters (if not provided, information needs
    to be stored in env. variables or in Giraffe's config file, [client]
    section.)
        --endpoint/-e ENDPOINT     Giraffe REST API endpoint (domain:port)
        --username/-u USERNAME
        --password/-p PASSWORD
        --tenant_id TENANT_ID
        --tenant_name TENANT_NAME
        --auth_url/-a AUTH_URL     Keystone authentification service (URL)

Examples:
    **TO BE DONE**
"""


from cement.core import foundation, controller, handler  # < cement 2.0.2
import requests                                          # < requests 0.14.2
import os
import inspect
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.cbook as cbook
from giraffe.client.api import GiraffeClient
from giraffe.client.formatter import Text, \
                                     JsonFormatter, CsvFormatter, TabFormatter
from giraffe.common.config import Config
from giraffe.common.auth import AuthProxy

import logging
logger = logging.getLogger("client")


class AbstractBaseController(controller.CementBaseController):
    """
    GiraffeClient's abstract base controller
    """

#   def __init__(self, *args, **kwargs):
#       super(AbstractBaseController, self).__init__(*args, **kwargs)

    class Meta:
        """
        Model that serves as a container for arguments and options
        common to all Giraffe CLI controllers
        """

        label = 'abstract'
        # aliases = [...]
        # stacked_on = ...
        # stacked_type = ...
        # hide = [True|False]
        # usage = ...
        # description = ...
        # epilog = ...

        _config = Config('giraffe.cfg')

        # command line arguments
        # ! Warning: os.getenv over config.get, i.e., environment variables
        #            override params defined in giraffe.cfg
        _credentials = [
            (['--username', '-u'], \
                dict(action='store', help='$OS_USERNAME', \
                     default=os.getenv('OS_USERNAME') or \
                             _config.get('client', 'user'))),
            (['--password', '-p'], \
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
                             _config.get('client', 'tenant_name')))
            ]

        _services = [
            (['--auth_url', '-a'], \
                dict(action='store', help='$OS_AUTH_URL', \
                     default=os.getenv('OS_AUTH_URL') or \
                             _config.get('auth', 'public_url'))),
            (['--endpoint', '-e'], \
                dict(action='store', help='Giraffe REST API endpoint (domain:port)', \
                     default=':'.join([_config.get('rest_api', 'host'), \
                                       _config.get('rest_api', 'port')])))
            ]

        _domains = [
            (['--host'], \
                dict(action='store', help='host name or ID',
                     default=None)),
            (['--project', '--proj'], \
                dict(action='store', help='project name or ID',
                     default=None)),
            (['--user'], \
                dict(action='store', help='user name or ID', \
                     default=None)),
            (['--instance', '--inst'], \
                dict(action='store', help='instance name or ID', \
                     default=None))
            ]

        _modifiers = [
            (['--start'], \
                dict(action='store', dest='start_time', help='', \
                     default=None)),
            (['--end'], \
                dict(action='store', dest='end_time', help='', \
                     default=None)),
            (['--min'], \
                dict(action='store_true', help='', \
                     default=None)),
            (['--max'], \
                dict(action='store_true', help='', \
                     default=None)),
            (['--avg'], \
                dict(action='store_true', help='', \
                     default=None)),
            (['--hourly'], \
                dict(action='store_true', dest='hourly_avg', help='hourly '
                     'averages of meter values within an period '
                     '[to be defined by --start and --end]', \
                     default=None)),
            (['--daily'], \
                dict(action='store_true', dest='daily_avg', help='daily '
                     'averages of meter values within an period '
                     '[to be defined by --start and --end]', \
                     default=None)),
            (['--sum'], \
                dict(action='store_true', help='', \
                     default=None)),
            (['--count'], \
                dict(action='store_true', help='', \
                     default=None)),
            (['--limit'], \
                dict(action='store', help='max. number of objects to be '
                     'retrieved', \
                     default=0)),
            (['--order'], \
                dict(action='store', help='ORDER (ASC [default] or DESC)', \
                     default=None)),
            ]

        _aggregations = [
            'min', 'max', 'avg', 'hourly_avg', 'daily_avg', 'sum', 'count'
            ]

        _filters = [
            'start_time', 'end_time', 'limit', 'order'
            ]

        _params = sum([
            _aggregations, _filters
            ],
            [])

        _formats = [
            # (['--jsn'], \
            #     dict(action='store_true', help='display output as plain JSON', \
            #         default=None)),
            (['--csv'], \
                 dict(action='store_true', help='output formatted as CSV', \
                      default=None)),
            (['--tab'], \
                 dict(action='store_true', help='output formatted as table', \
                      default=None))
            ]

        arguments = sum([_modifiers,
                         _formats,
                         _credentials,
                         _services],
                        [])

    # @end class Meta ---------------------------------------------------------

    @staticmethod
    def _exec_context():
        outerframe = inspect.getouterframes(inspect.currentframe())[-1]
        return os.path.basename(outerframe[1])

    def _client(self):
        #@[fbahr]: `dirty` hack, getting dict instance from self.pargs
        _kwargs = dict((k, v) for (k, v) in self.pargs._get_kwargs())
        return GiraffeClient(auth_token=AuthProxy.get_token(**_kwargs))

    def _params(self):
        params = {}
        for k, v in self.pargs._get_kwargs():
            if v and k in AbstractBaseController.Meta._params:
                if k in AbstractBaseController.Meta._aggregations:
                    params['aggregation'] = k
                else:
                    params[k] = v
        return params

    def _formatter(self):
        if self.pargs.tab:
            return TabFormatter
        elif self.pargs.csv:
            return CsvFormatter
        else:  # default:
            return JsonFormatter

    def _display(self, result):
        try:
            items = result.as_(Text, formatter=self._formatter())
            print '\n', '\n'.join(items) if items else items, '\n'
        except:
            # type(result) is unicode
            print '\n', result, '\n'

    def _except(self, cmd, exc):
        if isinstance(exc, (requests.exceptions.HTTPError)):
            print '%s:' % self._exec_context(), 'Bad request: %s' % exc

        elif isinstance(exc, (requests.exceptions.ConnectionError,
                              NotImplementedError)):
            print '%s: %s' % (self._exec_context(), exc)

        else:
            print '\n'.join(['usage: %s' % self._usage_text, \
                             'Try "%s --help" for more detailed illustrations.'
                             % (' '.join([self._exec_context(), cmd])
                                    if   cmd
                                    else self._exec_context())])

# end of class AbstractBaseController -----------------------------------------


class BaseController(AbstractBaseController):
    """
    GiraffeClient's base controller
    """

    class Meta:
        label = 'base'
        # aliases = ...
        # stacked_on = ...
        # stacked_type = ...
        hide = False
        usage = '%s <CMD> [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = 'Command-line interface to the Giraffe REST API.'
        epilog = 'Try "%s <CMD> --help" for help on a specific command.' \
                 % AbstractBaseController._exec_context()

    @controller.expose(hide=True)
    def default(self):
        self._except(None, NotImplementedError)

# end of class BaseController -------------------------------------------------


class QueryCMDController(AbstractBaseController):
    """
    GiraffeClient's REST query controller
    """

    class Meta:
        label = 'query'
        # aliases = ...
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = True
        usage = '%s QUERY [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        epilog = ''

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--path'], \
                dict(action='store', help='REST API path', \
                                          default=None))],
        #   AbstractBaseController.Meta._modifiers,
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        try:
            if not self.pargs.path:
                raise Exception()
            #   ^     Exception('error: query [-q/--query ...] not specified')
            result = self._client()._get(self.pargs.path)
            self._display(result)
        except Exception as e:
            self._except('QUERY', e)

# end of class QueryCMDController ---------------------------------------------


class HostCMDController(AbstractBaseController):
    """
    GiraffeClient's 'hosts' command controller
    """

    class Meta:
        label = 'hosts'
        aliases = ['host']
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = False
        usage = '%s HOSTS [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        # epilog = ...

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--name', '--id'], \
                dict(action='store', dest='uuid', help='host name or ID', \
                     default=None))],
        #   AbstractBaseController.Meta._modifiers,
            [(['--count'], \
                dict(action='store_true', help='', \
                     default=None))],
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        """
        cmd: hosts                  ~ route: /hosts
        cmd: hosts --[id|name] ...  ~ route: /hosts/[id|name]
        """
        try:
            result = self._client().get_host(self.pargs.uuid, self._params()) \
                        if   self.pargs.uuid \
                        else self._client().get_hosts(self._params())
            self._display(result)
        except Exception as e:
            self._except('HOSTS', e)

# end of class HostCMDController ----------------------------------------------


class ProjCMDController(AbstractBaseController):
    """
    GiraffeClient's 'projects' command controller
    """

    class Meta:
        label = 'projects'
        aliases = ['proj']
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = False
        usage = '%s PROJECTS [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        # epilog = ...

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--name', '--id'], \
                dict(action='store', dest='uuid', help='project name or ID', \
                     default=None))],
        #   AbstractBaseController.Meta._modifiers,
            [(['--count'], \
                dict(action='store_true', help='', \
                     default=None))],
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        """
        cmd: projects                  ~ route: /projects
        cmd: projects --[id|name] ...  ~ route: /projects/[id|name]
        """
        try:
            if self.pargs.uuid:
                # self._client().get_project(self.pargs.uuid, self._params())
                raise NotImplementedError('Route /projects/[id|name] '
                                          'not (yet) implemented.')
            result = self._client().get_projects(self._params())
            self._display(result)
        except Exception as e:
            self._except('PROJECTS', e)

# end of class ProjCMDController ----------------------------------------------


class UserCMDController(AbstractBaseController):
    """
    GiraffeClient's 'users' command controller
    """

    class Meta:
        label = 'users'
        aliases = ['user']
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = False
        usage = '%s USERS [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        # epilog = ...

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--name', '--id'], \
                dict(action='store', dest='uuid', help='user name or ID', \
                     default=None))],
        #   AbstractBaseController.Meta._modifiers,
            [(['--count'], \
                dict(action='store_true', help='', \
                     default=None))],
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        """
        cmd: users                  ~ route: /users
        cmd: users --[id|name] ...  ~ route: /users/[id|name]
        """
        try:
            if self.pargs.uuid:
                # client().get_user(self.pargs.uuid, self._params())
                raise NotImplementedError('Route /users/[id|name] '
                                          'not (yet) implemented.')
            result = self._client().get_users(self._params())
            self._display(result)
        except Exception as e:
            self._except('USERS', e)

# end of class UserCMDController ----------------------------------------------


class InstCMDController(AbstractBaseController):
    """
    GiraffeClient's 'instances' command controller
    """

    class Meta:
        label = 'instances'
        aliases = ['inst']
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = False
        usage = '%s INSTANCES [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        # epilog = ...

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--name', '--id'], \
                dict(action='store', dest='uuid', help='instance name or ID', \
                     default=None))],
        #   AbstractBaseController.Meta._domains,
            [(['--project', '--proj'], \
                dict(action='store', help='project name or ID', \
                     default=None))],
        #   AbstractBaseController.Meta._modifiers,
            [(['--count'], \
                dict(action='store_true', help='', \
                     default=None))],
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        """
        cmd: instances                  ~ route: /instances
        cmd: instances --[id|name] ...  ~ route: /instances/[id|name]
        cmd: instances --project ...    ~ route: /projects/pid/instances
        """
        target =    ('get_instance', self.pargs.uuid) \
                        if   self.pargs.uuid \
                        else None \
                 or ('get_proj_instances', self.pargs.project) \
                        if   self.pargs.project \
                        else None \
                 or ('get_instances', None)

        try:
            method = getattr(self._client(), target[0])
            params = filter(bool, [target[1], self._params()])
            result = method(*params)
            self._display(result)
        except Exception as e:
            self._except('INSTANCES', e)

# end of class InstCMDController ----------------------------------------------


class MeterCMDController(AbstractBaseController):
    """
    GiraffeClient's 'meters' command controller
    """

    class Meta:
        label = 'meters'
        aliases = ['meter']
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = False
        usage = '%s METERS [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        # epilog = ...

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--id'], \
                dict(action='store', dest='uuid', help='meter ID', \
                     default=None))],
            AbstractBaseController.Meta._domains,
        #   AbstractBaseController.Meta._modifiers,
            [(['--count'], \
                dict(action='store_true', help='', \
                     default=None))],
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        """
        cmd: meters                ~ route: /meters
        cmd: meters --id ...       ~ route: /meters/id
        cmd: meters --host ...     ~ route: /host/hid/meters/
        cmd: meters --project ...  ~ route: /projects/pid/meters/
        """
        target =    ('get_meter', self.pargs.uuid) \
                        if   self.pargs.uuid \
                        else None \
                 or ('get_host_meters', self.pargs.host) \
                        if   self.pargs.host \
                        else None \
                 or ('get_proj_meters', self.pargs.project) \
                        if   self.pargs.project \
                        else None \
                 or ('get_meters', None)

#                or ('...', self.pargs.user) \
#                       if   self.pargs.user \
#                       else None \
#                or ('...', self.pargs.instance)
#                       if   self.pargs.instance \
#                       else None \

        try:
            method = getattr(self._client(), target[0])
            params = filter(bool, [target[1], self._params()])
            result = method(*params)
            self._display(result)
        except Exception as e:
            self._except('METERS', e)

# end of class MeterCMDController ---------------------------------------------


class RecordCMDController(AbstractBaseController):
    """
    GiraffeClient's 'records' command controller
    """

    class Meta:
        label = 'records'
        aliases = ['record']
        # stacked_on = 'base'
        stacked_type = 'nested'
        hide = False
        usage = '%s RECORDS [--arguments] [--options]' \
                % AbstractBaseController._exec_context()
        description = ''
        # epilog = ...

        # Note: "You can not override the Meta.arguments in a sub-class or you
        #        overwrite the shared arguments."
        # - https://cement.readthedocs.org/en/latest/examples/abstract_base_controllers/
        arguments = sum([
            [(['--id'], \
                dict(action='store', dest='uuid', help='record ID', \
                     default=None))],
            AbstractBaseController.Meta._domains,
            [(['--meter'], \
                dict(action='store', dest='meter', help='meter ID', \
                     default=None))],
            AbstractBaseController.Meta._modifiers,
            AbstractBaseController.Meta._formats,
            AbstractBaseController.Meta._credentials,
            AbstractBaseController.Meta._services],
            [])

    @controller.expose(hide=True)
    def default(self):
        """
        cmd: records                             ~ route: /records
        cmd: records --id ...                    ~ route: /records/id
        cmd: records --host ... --meter ...      ~ route: /host/hid/meters/mid/records/
        cmd: records --project ... --meter ...   ~ route: /projects/pid/records/
        cmd: records --user ... --meter ...      ~ route: /user/uid/records/
        cmd: records --instance ... --meter ...  ~ route: /instances/iid/meters/mid/records/
        """

        target =    ('get_record', self.pargs.uuid) \
                        if   self.pargs.uuid \
                        else None \
                 or ('get_host_meter_records', self.pargs.host, self.pargs.meter) \
                        if   self.pargs.host and self.pargs.meter \
                        else None \
                 or ('get_proj_meter_records', self.pargs.project, self.pargs.meter) \
                        if   self.pargs.project and self.pargs.meter \
                        else None \
                 or ('get_user_meter_records', self.pargs.user, self.pargs.meter) \
                        if   self.pargs.user and self.pargs.meter \
                        else None \
                 or ('get_inst_meter_records', self.pargs.instance, self.pargs.meter) \
                        if   self.pargs.instance and self.pargs.meter \
                        else None \
                 or ('get_records', None)

        try:
            method = getattr(self._client(), target[0])
            params = filter(bool, target[1:] + (self._params(),))
            result = method(*params)
            self._display(result)
        except Exception as e:
            self._except('RECORDS', e)

# end of class RecordCMDController --------------------------------------------


class GiraffeClientApp(foundation.CementApp):
    class Meta:
        label = 'giraffe-client'

    def __init__(self, **kwargs):
        try:
            super(GiraffeClientApp, self).__init__(**kwargs)

            # registering controllers
            handler.register(BaseController)
            handler.register(QueryCMDController)
            handler.register(HostCMDController)
            handler.register(ProjCMDController)
            handler.register(UserCMDController)
            handler.register(InstCMDController)
            handler.register(MeterCMDController)
            handler.register(RecordCMDController)

            # base_controller = BaseController  # < default: Controller w/
                                                #            label 'base'

        except Exception as e:
            print e


def main():

    # creating an application
    app = GiraffeClientApp()

    try:
        # setting up and running the application
        app.setup()
        app.run()
    except Exception as e:
        logger.exception('%s' % e)
    finally:
        # closing the application
        app.close()


if __name__ == '__main__':
    main()
