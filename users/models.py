import requests, datetime
from flask import request
from flask_login import UserMixin
from wardrobe import db
from config import CONNECTION_ERRORS


def get_srv_ip():
    _ip = {}
    try:
        _ip = requests.get('http://2ip.ru', headers={'user-agent': 'curl'}, timeout=1)
    except CONNECTION_ERRORS:
        _ip['status_code'] = 404

    if getattr(_ip, 'status_code', 0) == 200:
        _ip = _ip.text.replace('\n', '')
    else:
        _ip = '46.39.56.60'

    return _ip


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    # todo add true format for geo column
    geo = db.Column(db.String(128))
    lang = db.Column(db.String(5))
    ip = db.Column(db.String(15))
    role = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
    clothes = db.relationship('Clothes')
    registered = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, username):
        self.username = username
        self.password = ''
        self.email = f'{username}@mail.debug'
        self.lang = ''
        self.get_language()
        self.ip = ''
        self.get_user_ip()
        self.full_geo = {}
        self.geo = ''
        self.get_user_geo()

    def get_language(self):
        try:
            self.lang = request.accept_languages[0][0]
        except KeyError:
            self.lang = 'ru'

    def set_user_password(self, password):
        self.password = password

    def get_user_ip(self):
        try:
            _ip = request.environ['HTTP_X_FORWARDED_FOR']
        except KeyError:
            _ip = request.environ['REMOTE_ADDR']
        else:
            _ip = '46.39.56.60'

        _ip_bit = _ip.split('.')

        if (_ip_bit[0] == '192') and (_ip_bit[1] == '168'):
            _ip = get_srv_ip()
        elif (_ip_bit[0] == '172') and (_ip_bit[1] in range(16, 32, 1)):
            _ip = get_srv_ip()
        elif _ip_bit[0] == '10':
            _ip = get_srv_ip()
        elif _ip_bit[0] == '127':
            _ip = get_srv_ip()

        self.ip = _ip

    def get_user_geo(self):
        from config import GEOIP_APIKEY, GEOIP_URL
        params = {
            'apiKey': GEOIP_APIKEY,
            'ip': self.ip
        }

        try:
            self.full_geo = requests.get(GEOIP_URL, params, timeout=1)
        except CONNECTION_ERRORS:
            self.full_geo['status_code'] = 404

        if getattr(self.full_geo, 'status_code', 0) == 200:
            self.full_geo = self.full_geo.json()
            self.geo = '{},{}'.format(self.full_geo['city'], self.full_geo['country_code2'])
        else:
            self.full_geo = {}
            self.geo = 'Cant determine your current location.'

    class UserToken(db.Model):
        __tablename__ = 'user_tokens'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        token = db.Column(db.String(16), unique=True)
        type = db.Column(db.Integer)
        issue = db.Column(db.DateTime, default=datetime.datetime.utcnow)
        expire = db.Column(db.DateTime)

        def __init__(self, user_id, token_type='user', token_expire=datetime.datetime(2099, 1, 1, 0, 0, 0)):
            self.user_id = user_id
            self.type = token_type
            self.expire = token_expire

            if token_type == 'user':
                from secrets import token_urlsafe
                self.token = token_urlsafe(16)
            if token_type == 'totp':
                from pyotp import random_base32
                self.token = random_base32(16)


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(64), unique=True, index=True)
    # rights = db.Column(db.String(128))
