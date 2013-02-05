 from keystoneclient.v2_0 import client as ksclient


class AuthProxy(object):

    @staticmethod
    def get_token(credentials=None, **kwargs):
        params = {}

        if credentials:
            params.update(credentials)

        params.update(kwargs)

        # params['username'] = kwargs['username']  # os.getenv('OS_USERNAME')
        # params['password'] = kwargs['password']  # os.getenv('OS_PASSWORD')
        # params['tenant_id'] = kwargs['tenant_id']  # os.getenv('OS_TENANT_ID'),
        # params['tenant_name'] = kwargs['tenant_name']  # os.getenv('OS_TENANT_NAME')
        # params['auth_url'] = params['auth_url']  # os.getenv('OS_AUTH_URL')
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
