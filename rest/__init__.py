import json

from rest.handlers import APIHandlers
from rest.utils import token_auth_required
from wardrobe import db
from users.models import User
from clothes.models import Clothes, import_default_clothe_types


def response_wrapper(*args):
    _resp = {'code': 404, 'body': {}}
    if args == ():
        args = (404, ('msg', 'Not found'))

    _resp['code'] = args[0]
    for block in args[1:]:
        block_name = block[0]
        block_data = block[1]
        _resp['body'][block_name] = block_data

    return json.dumps(_resp)


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
        return response_wrapper(*resp)
