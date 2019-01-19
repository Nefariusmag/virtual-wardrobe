import requests
from flask import request
from flask_login import UserMixin
from wardrobe import db


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
    clothes = db.relationship('Clothes')

    def __init__(self, username):
        self.username = username
        self.password = ''
        self.email = f'{username}@mail.debug'
        self.lang = self.get_language()
        self.ip = self.get_user_ip()
        self.full_geo = self.get_user_geo()
        self.geo = '{},{}'.format(self.full_geo['city'], self.full_geo['country_code2'])

    def get_language(self):
        try:
            return request.accept_languages[0][0]
        except:
            return 'ru'

    def set_user_password(self, password):
        self.password = password

    def get_user_ip(self):
        addr_header = 'HTTP_X_FORWARDED_FOR'
        try:
            if request.environ.get(addr_header,0) == 0:
                addr_header = 'REMOTE_ADDR'
            _ip = request.environ[addr_header]
        except:
            _ip = '46.39.56.60'

        _ip_bit = _ip.split('.')

        if (_ip_bit[0] == '192') and (_ip_bit[1] == '168'):
            _ip = self.get_srv_ip()
        elif (_ip_bit[0] == '172') and (_ip_bit[1] in range(16, 32, 1)):
            _ip = self.get_srv_ip()
        elif _ip_bit[0] == '10':
            _ip = self.get_srv_ip()
        elif _ip_bit[0] == '127':
            _ip = self.get_srv_ip()

        return _ip

    def get_srv_ip(self):
        _ip = requests.get('https://api.ipify.org')
        if _ip.status_code == 200:
            _ip = _ip.text
        else:
            _ip = '46.39.56.60'

        return _ip

    def get_user_geo(self):
        from config import GEOIP_APIKEY, GEOIP_URL
        params = {
            'apiKey': GEOIP_APIKEY,
            'ip': self.ip
        }

        user_geo = requests.get(GEOIP_URL, params)
        if user_geo.status_code == 200:
            user_geo = user_geo.json()
        else:
            user_geo = {'country_code2': 'RU', 'city': 'Moscow'}

        return user_geo
