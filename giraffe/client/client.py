"""
usage: ./start_client -r=<query>
                            ^ e.g., <query>="/hosts/<host-id>"
"""

__author__  = 'fbahr'
__version__ = '0.1.1'
__date__    = '2012-12-13'


from cement.core import foundation, controller  # < cement 2.0.2
import requests                                 # < requests 0.14.2
import json
from giraffe.common.config import Config

import logging
logger = logging.getLogger("client")


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


        # default config options
        # config_defaults = {}


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

            r = requests.get(url, auth=(self.pargs.username, self.pargs.password))
            logger.debug('HTTP response status code: %s' % r.status_code)

            r.raise_for_status()

            if self.pargs.csv:
                offset = True
                header = []
                for msg in r.json:
                    line = []
                    for key, val in msg.iteritems():
                        if offset:
                            header.append(key)
                        line.append(val)
                    if offset:
                        print '\t'.join(header)
                        offset = False
                    print '\t'.join(line)
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


class GiraffeClient(foundation.CementApp):
    class Meta:
        label = 'giraffe-client'
        base_controller = BaseController()

#   def __init__(self, **kwargs):
#       foundation.CementApp.__init__(self, kwargs)



def main():
    #create an application
    app = GiraffeClient()

    try:
        # setup the application
        app.setup()
        app.run()
    except Exception as e:
        print e
    finally:
        # close the application
        app.close()


if __name__ == '__main__':
    main()