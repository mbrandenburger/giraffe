from keystoneclient.v2_0 import client as ksclient


class AuthProxy(object):

    @staticmethod
    def get_token(**params):
        _ksclient = ksclient.Client(username=params.get('username'),
                                    password=params.get('password'),
                                    tenant_id=params.get('tenant_id'),
                                    tenant_name=params.get('tenant_name'),
                                    auth_url=params.get('auth_url'),
                                    insecure=params.get('insecure', False))

        return _ksclient.auth_token
