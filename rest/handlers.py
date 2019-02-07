from inspect import getargspec
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

    @token_auth_required(['service', 'admin'])
    def handler_new_user(self):
        if (self.params['method'] == 'POST') and (self.params['data']):
            mb_user = self.params['data'].get('user', 0)
            if mb_user.get('password', 0):
                user_req_args = {}
                user_req_args_list = getargspec(User).args[1:]
                for k in user_req_args_list:
                    if mb_user.get(k, 0) == 0:
                        return []
                    user_req_args[k] = mb_user[k]

                if User.query.filter(
                        (User.username == user_req_args['username']) | (User.email == user_req_args['email'])
                ).first() is None:
                    new_user = User(**user_req_args)
                    new_user.set_user_password(mb_user.get('password'))
                    new_user.role = db.session.query(UserRole.id).filter(UserRole.role == 'user').first().id
                    db.session.add(new_user)
                    db.session.commit()
                    db.session.add(new_user.UserToken(user_id=new_user.id))
                    db.session.add(new_user.UserToken(user_id=new_user.id, token_type='totp'))
                    db.session.commit()
                    return [200, ('user', model2dict(new_user))]
            else:
                return []

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
                    if cv and (k not in ['id', 'username', 'password']):
                        setattr(user, k, v)
                        need_update = 1

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
                    clothes = [model2dict(clothe) for clothe in user.clothes if
                               clothe.id in [x['id'] for x in n_clothes]]
                    return [200, ('msg', "Clothes's data is updated"), ('clothes', clothes)]

        return []
