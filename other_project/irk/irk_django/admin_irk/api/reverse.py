import urllib

from rest_framework.reverse import reverse as base_reverse


def reverse(*args, **kwargs):
    url = base_reverse(*args, **kwargs)

    request = kwargs.get('request')
    if request:
        params = {}
        http_request = request._request.GET
        for field in ('format', 'token'):
            if field in http_request:
                params[field] = http_request[field]

        url = '?'.join([url, urllib.urlencode(params)])

    return url
