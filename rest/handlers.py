from inspect import getfullargspec
from rest.utils import token_auth_required, model2dict

from wardrobe import db
from users.models import User, UserRole
from clothes.models import Clothes


class APIHandlers(object):

    def __init__(self, *args, **kwargs):
        self.resp = dict(code=404, msg='Not found')
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
        return self.resp

    @token_auth_required(['service', 'admin'])
    def handler_new_user(self):
        if (self.params['method'] == 'POST') and (self.params['data']):
            mb_user = self.params['data']
            if mb_user.get('password', 0) and mb_user.get('username', 0):
                new_user_params = {}
                user_params = getfullargspec(User)
                user_def_params_list = user_params.args[-len(user_params.defaults):]
                user_req_params_list = user_params.args[1:-len(user_params.defaults)]
                self.resp['forms'] = []
                for k in user_req_params_list:
                    v = mb_user.get(k, '')
                    if v:
                        new_user_params[k] = v
                        continue
                    self.resp['forms'].append(k)

                if self.resp['forms']:
                    self.resp['msg'] = 'Fill in required forms'
                    return self.resp

                for k in user_def_params_list:
                    v = mb_user.get(k, '')
                    new_user_params[k] = v

                self.resp.pop('forms')

                if User.query.filter(
                        (User.username == new_user_params['username']) | (User.email == new_user_params['email'])
                ).first() is None:
                    new_user = User(**new_user_params)
                    new_user.set_user_password(mb_user.get('password'))
                    new_user.role = db.session.query(UserRole.id).filter(UserRole.role == 'user').first().id
                    db.session.add(new_user)
                    db.session.add(new_user.UserToken(username=new_user.username))
                    db.session.add(new_user.UserToken(username=new_user.username, token_type='totp'))
                    db.session.commit()
                    self.resp['code'] = 200
                    self.resp['msg'] = 'User created'
                    self.resp['user'] = dict(id=new_user.id)
                else:
                    self.resp['code'] = 403
                    self.resp['msg'] = 'User with this username or email is already exist'

        return self.resp

    @token_auth_required()
    def handler_user(self):
        user = User.query.filter(User.id == self.params['uid']).first()

        if user:
            if self.params['method'] == 'GET':
                user = model2dict(user, ['id', 'password'])
                self.resp['code'] = 200
                self.resp['msg'] = 'OK'
                self.resp['user'] = user

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
                    self.resp['code'] = 200
                    self.resp['msg'] = 'User updated'
                    self.resp['user'] = user

        return self.resp

    @token_auth_required()
    def handler_clothes(self):
        user = User.query.filter(User.id == self.params['uid']).first()
        if user:
            if self.params['method'] == 'GET':
                if user.clothes:
                    clothes = [model2dict(clothe) for clothe in user.clothes]
                else:
                    clothes = []
                self.resp['code'] = 200
                self.resp['msg'] = 'OK'
                self.resp['clothes'] = clothes

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
                    self.resp['code'] = 200
                    self.resp['msg'] = 'Clothes data updated'
                    self.resp['clothes'] = clothes

        return self.resp
