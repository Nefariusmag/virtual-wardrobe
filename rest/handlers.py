from rest.utils import token_auth_required, model2dict

from wardrobe import db
from users.models import User, UserRole
from clothes.models import Clothes


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

    @token_auth_required()
    def handler_user(self):
        user = User.query.filter(User.id == self.params['uid']).first()

        if user:
            if self.params['method'] == 'GET':
                user = model2dict(user, ['id', 'password'])
                return [200, ('user', user)]

            if (self.params['method'] == 'POST') and (self.params['data']):
                # TODO: Add input validation for each field
                need_update = 0
                for k, v in self.params['data'].items():
                    cv = getattr(user, k, 0)
                    if cv and (k not in ['id', 'username']):
                        setattr(user, k, v)
                        need_update = 1
                    else:
                        break

                if need_update:
                    db.session.commit()
                    user = model2dict(user, ['id', 'password'])
                    return [200, ('msg', "User's data is updated"), ('user', user)]

        return []

    @token_auth_required()
    def handler_clothes(self):
        user = User.query.filter(User.id == self.params['uid']).first()
        if user:
            if self.params['method'] == 'GET':
                if user.clothes:
                    clothes = [model2dict(clothe) for clothe in user.clothes]
                else:
                    clothes = []
                return [200, ('user', user.username), ('clothes', clothes)]

            if (self.params['method'] == 'POST') and (self.params['data']):
                need_update = 0
                n_clothes = self.params['data'].get('clothes', 0)
                if n_clothes:
                    for n_clothe in n_clothes:
                        n_clothe_id = n_clothe.get('id', 0)
                        if n_clothe_id:
                            c_clothe = [x for x in user.clothes if x.id == int(n_clothe_id)][0]
                            for k, v in n_clothe.items():
                                cv = getattr(c_clothe, k, 0)
                                if cv and (k not in ['id']):
                                    setattr(c_clothe, k, v)
                                    need_update = 1

                if need_update:
                    db.session.commit()
                    clothes = [model2dict(clothe) for clothe in user.clothes if clothe.id in [x['id'] for x in n_clothes]]
                    return [200, ('msg', "Clothes's data is updated"), ('clothes', clothes)]

        return []
