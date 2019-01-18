import json

from wardrobe import db
from users.models import User
from clothes.models import Clothes, import_default_clothe_types


def response_wrapper(*args, **kwargs):
    _resp = {}
    code = 404
    msg = {'Not found'}
    if args != ():
        code = args[0]
        msg = {}
        for block in args[1:]:
            block_name = block[0]
            # block_data = block[1]
            for block_data in block[1]:
                msg.update({block_name: block_data})

    _resp.update({'code': code})
    _resp.update({'body': msg})

    return json.dumps(_resp)


class WardrobeAPI(object):

    def __init__(self, db, *args):
        self.db = db
        self.params = dict(args[0])
        self.headers = dict(args[1])
        self.response = self.response()

    def check_token(self, _token):
        user_id = db.session.query(User.UserToken.user_id). \
            filter(User.UserToken.token == _token). \
            first()
        if (user_id != []) and user_id:
            user = db.session.query(User.id, User.username).filter(
                User.id.in_(
                    user_id
                )
            ).all()
        return user

    def response(self):
        resp = [200, ('msg', 'Hello world!')]
        token = self.params.get('TOKEN', 0)
        if token:
            user = self.check_token(token)
            resp.append(('user', (('id', user.id), ('name', user.username))))
        return response_wrapper(*resp)
