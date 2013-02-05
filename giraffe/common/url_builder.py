class URLBuilder(object):

    @staticmethod
    def build(protocol='http', endpoint, path, params=None):
        """
        Aux function to build a URL (string) from protocol, endpoint, path,
        and parameters.
        """
        url = ''.join([protocol, '://', endpoint, path, '?' if params else ''])
        if params:
            url += '&'.join(["%s=%s" % (k, str(v)) for k, v in params.iteritems()])
        return url
