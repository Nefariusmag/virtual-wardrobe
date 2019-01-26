from rest.utils import token_auth_required, model2dict

from wardrobe import db
from users.models import User, UserRole
from clothes.models import Clothes, import_default_clothe_types


class APIHandlers(object):

    def __init__(self, *args, **kwargs):
        self.params = {}
        if args:
            for arg in args:
                for name, data in arg.items():
                    self.params[str(name).lower().replace('-', '_')] = data
        if kwargs:
            for name, data in kwargs.items():
                self.params[str(name).lower().replace('-', '_')] = data

    def __call__(self):
        handler = 'handler_{}'.format(self.params.get('command', 0))
        handlers_list = [h for h in dir(self) if callable(getattr(self, h)) and h.startswith("handler_")]
        if handler in handlers_list:
            handler_response = getattr(self, handler)()
            return handler_response
        return []

    @token_auth_required
    def handler_user(self):
        user = User.query.filter(User.id == self.params['user_id']).one()

        if self.params['method'] == 'GET':
            user = model2dict(user, ['password'])
            return [200, ('user', user)]

        if (self.params['method'] == 'POST') and (self.params['data']):
            # TODO: Add input validation for each field
            need_update = 0
            for k, v in self.params['data'].items():
                if getattr(user, k, 0) and k not in ['id']:
                    setattr(user, k, v)
                    need_update = 1
                else:
                    break

            if need_update:
                db.session.commit()
                return [200, ('msg', "User's data is updated")]

        return []
