from functools import wraps
import pyotp

from wardrobe import db
from users.models import User, UserRole


def token_auth_required(auth_roles=[]):
    def decorator(func):
        @wraps(func)
        def wrapped_handler(*args, **kwargs):
            hnd_params = getattr(args[0], 'params', {})
            resp = getattr(args[0], 'resp', {})
            if hnd_params:
                mb_uid = hnd_params.get('uid', 0)
                if mb_uid:
                    mb_uid = int(mb_uid)
                mb_token = hnd_params.pop('token', 0)

                if mb_token:
                    un = getattr(
                        User.UserToken.query.filter(
                            (User.UserToken.token == mb_token) & (User.UserToken.type == 'user')
                        ).first(),
                        'username', 0
                    )
                    uid = getattr(
                        User.query.filter(User.username == un).first(),
                        'id',
                        0
                    )
                    if uid:
                        uid_user = User.query.filter(User.id == uid).first()
                        uid_user_role = getattr(UserRole.query.filter(UserRole.id == uid_user.role).first(), 'role', '')
                        hnd_params['init_role'] = uid_user_role
                        if auth_roles:
                            if uid_user_role not in auth_roles:
                                return resp
                        if mb_uid:
                            if uid_user_role in ['admin', 'service']:
                                return func(*args, **kwargs)
                            if mb_uid and uid == mb_uid:
                                return func(*args, **kwargs)
                            else:
                                return resp
                        else:
                            hnd_params['uid'] = str(uid)

                        return func(*args, **kwargs)
            return resp

        return wrapped_handler

    return decorator


def model2dict(model, attr_excl=[]):
    from sqlalchemy import inspect

    model_props = []
    for attr in getattr(inspect(model), 'attrs', []):
        if (type(getattr(attr, 'value')) in [str, int, bool]) and attr.key not in attr_excl:
            model_props.append(attr.key)
    model_dict = {x: getattr(model, x, '') for x in model_props}

    return model_dict


def row2dict(row):
    row_in_dict = {}
    for col in getattr(row, '_fields', ()):
        row_in_dict.update({col: getattr(row, col)})
    return row_in_dict
