__author__  = 'fbahr'
__version__ = '0.1'
__date__    = '2012-12-02'

from cement.core impo__author__  = 'fbahr'
__version__ = '0.1'
__date__    = '2012-12-02'

from cement.core import backend, foundation, hook # < cement 2.0.2
import requests                                   # < requests 0.14.2


# set default config options
defaults = backend.defaults('giraffe-client')
defaults['giraffe-client']['debug'] = False
defaults['giraffe-client']['auth'] = None # OS_AUTH_URL
defaults['giraffe-client']['username'] = None # OS_USERNAME
defaults['giraffe-client']['password'] = None # OS_PASSWORD
defaults['giraffe-client']['tenant_id']  = None
defaults['giraffe-client']['tenantname'] = None

# create an application
app = foundation.CementApp('giraffe-client', config_defaults=defaults)


try:
    # setup the application
    app.setup()

    # add arguments
    app.args.add_argument('-a', '--auth_url', action='store', metavar='',
                          help='OS_AUTH_URL')
    app.args.add_argument('-u', '--username', action='store', metavar='',
                          help='OS_USERNAME')
    app.args.add_argument('-p', '--password', action='store', metavar='',
                          help='OS_PASSWORD')
    app.args.add_argument('-tid', '--tenant_id', action='store', metavar='',
                          help='OS_TENANT_ID')
    app.args.add_argument('-tname', '--tenantname', action='store', metavar='',
                          help='OS_TENANT_NAME')

    app.run()

    # application logic    
    r = requests.get("",
                     auth=(app.pargs.user, app.pargs.passname))

finally:
    # close the application
    app.close()
