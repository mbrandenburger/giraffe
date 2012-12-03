__author__  = 'fbahr'
__version__ = '0.1'
__date__    = '2012-12-02'

from cement.core import backend, foundation, controller, handler # < cement 2.0.2
import requests                                                  # < requests 0.14.2

# default config options
# defaults = backend.defaults('giraffe-client')
# defaults['giraffe-client']['debug']       = False
# defaults['giraffe-client']['auth_url']    = None # OS_AUTH_URL
# defaults['giraffe-client']['username']    = None # OS_USERNAME
# defaults['giraffe-client']['password']    = None # OS_PASSWORD
# defaults['giraffe-client']['tenant_id']   = None
# defaults['giraffe-client']['tenant_name'] = None


# an application base controller
class BaseController(controller.CementBaseController):
    class Meta:
        label = 'base-controller'
        # description = ''

        # default config options
        config_defaults = dict(
            auth        = None, # OS_AUTH_URL
            username    = None, # OS_USERNAME
            password    = None, # OS_PASSWORD
            tenant_id   = None,
            tenant_name = None
            )

        # command line arguments
        arguments = [
            (['-a',     '--auth_url'],    dict(action='store', help='OS_AUTH_URL')),
            (['-u',     '--username'],    dict(action='store', help='OS_USERNAME')),
            (['-p',     '--password'],    dict(action='store', help='OS_PASSWORD')),
            (['-tid',   '--tenant_id'],   dict(action='store', help='OS_TENANT_ID')),
            (['-tname', '--tenant_name'], dict(action='store', help='OS_TENANT_NAME'))
            ]
        #   ...
        #   (['-F',      '--FLAG'],       dict(action='store_true', help='...'))
        #   ...
        
        @controller.expose(help='')
        def GET(self):
            # self.log.info("Inside base.command1 function.")
                r = requests.get("",
                     auth=(app.pargs.user, app.pargs.passname))


class GiraffeClient(foundation.CementApp):
    class Meta:
        label = 'giraffe-client'
        # description = ''        
        base_controller = BaseController()


    def __init__(self, **kwargs):
        foundation.CementApp.__init(kwargs)


# create an application
app = GiraffeClient('giraffe-client', config_defaults=defaults)

try:
    # setup the application
    app.setup()
    app.run()

finally:
    # close the application
    app.close()
