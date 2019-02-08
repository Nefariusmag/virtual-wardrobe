import json

from rest.handlers import APIHandlers
from rest.utils import token_auth_required


def response_wrapper(**kw):
    if kw.get('code', 0):
        return json.dumps(kw)
    return json.dumps(dict(code=500))


class WardrobeAPI(object):

    def __init__(self, db, *args, **kwargs):
        self.db = db
        self.params = dict(args[0])
        self.params['version'] = kwargs['v']
        self.params['command'] = kwargs['apicmd']
        self.params['method'] = kwargs['method']
        self.params['data'] = args[2] or {}
        self.headers = dict(args[1])
        self.response = self.response()

    def response(self):
        handler = APIHandlers(self.params, self.headers)
        resp = handler()
        return response_wrapper(**resp)
