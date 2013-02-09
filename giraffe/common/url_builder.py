class URLBuilder(object):

    @staticmethod
    def build(protocol='http', endpoint='127.0.0.1', path='/', params=None):
        """
        Aux function to build a URL (string) from protocol, endpoint, path,
        and parameters.
        """
        url = ''.join([protocol, '://', endpoint, path, '?' if params else ''])
        if params:
            url += '&'.join(["%s=%s" % (k, str(v)) \
                                       for k, v in params.iteritems() if v])
        return url

    @staticmethod
    def build_path(*path):
        path = '/'.join([section if section else 'UNDEFINED' \
                         for section in path])
        return path
