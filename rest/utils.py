from functools import wraps

from wardrobe import db
from users.models import User, UserRole


def token_auth_required(func):
    @wraps(func)
    def decorated_handler(*args, **kwargs):
        hnd_params = getattr(args[0], 'params', {})
        if hnd_params:
            uid = int(hnd_params.get('user_id', 0))
            if uid:
                if User.query.filter(User.id == uid).first():
                    token = hnd_params.get('token', 'FALSE')
                    tuid = getattr(User.UserToken.query.
                                   filter(User.UserToken.token == token).
                                   first(), 'user_id', 0)
                    if tuid:
                        # TODO: Validate if it is a service user token
                        if int(tuid) == int(uid):
                            return func(*args, **kwargs)

        return []

    return decorated_handler


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
