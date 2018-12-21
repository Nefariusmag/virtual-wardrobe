import requests
from flask import request
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password, uid):
        self.uid = uid
        self.username = username
        self.password = password
        self.lang = request.accept_languages[0][0]
        self.ip = self.get_user_ip()
        self.geo = self.get_user_geo()
        self.city = '{},{}'.format(self.geo['city'], self.geo['country_code2'])

    def get_id(self):
        return self.uid

    def get_user_ip(self):
        _ip = request.environ['REMOTE_ADDR']
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
        # todo add try to take error if api.ipify.org is not working
        _ip = requests.get('https://api.ipify.org')
        if _ip.status_code == 200:
            _ip = _ip.text

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

        return user_geo


class UsersRepository:
    def __init__(self):
        self.users = dict()
        self.users_id_dict = dict()
        self.identifier = 0

    def save_user(self, user):
        self.users_id_dict.setdefault(user.uid, user)
        self.users.setdefault(user.username, user)

    def get_user(self, username):
        return self.users.get(username)

    def get_user_by_id(self, userid):
        return self.users_id_dict.get(userid)

    def next_index(self):
        self.identifier += 1
        return self.identifier
