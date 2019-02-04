from functools import wraps
import pyotp

from wardrobe import db
from users.models import User, UserRole


def token_auth_required(func):
    @wraps(func)
    def decorated_handler(*args, **kwargs):
        hnd_params = getattr(args[0], 'params', {})
        if hnd_params:
            uid = int(hnd_params.get('user_id', 0))
            mb_service = hnd_params.get('service', 0)
            mb_token = hnd_params.get('token', 0)
            if mb_service:
                mb_user = User.query.filter(User.username == mb_service).first()
                if UserRole.query.filter(UserRole.id == mb_user.role).filter(UserRole.role == 'service').first():
                    uid = getattr(mb_user, 'id', 0)
                else:
                    uid = 0
            if uid and (User.query.filter(User.id == uid).first()):
                if mb_token:
                    usr_token = getattr(User.UserToken.query.filter(
                        (User.UserToken.user_id == uid) & (User.UserToken.type == 'user')).first(), 'token', 0)
                    if len(mb_token) == 6:
                        usr_token = User.UserToken.query.filter(
                            (User.UserToken.user_id == uid) & (User.UserToken.type == 'totp')).first()
                        usr_token = pyotp.TOTP(usr_token.token).now()
                    if usr_token == mb_token:
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