import requests
from flask import Flask, request, abort, redirect, render_template
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username, password, id, active=True):
        self.id = id
        self.username = username
        self.password = password
        self.active = active
        self.lang = request.accept_languages[0][0]
        self.ip = self.get_user_ip()
        self.geo = self.get_user_geo()
        self.city = '{},{}'.format(self.geo['city'], self.geo['country_code2'])

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.username, key='secret_key')

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
        self.users_id_dict.setdefault(user.id, user)
        self.users.setdefault(user.username, user)

    def get_user(self, username):
        return self.users.get(username)

    def get_user_by_id(self, userid):
        return self.users_id_dict.get(userid)

    def next_index(self):
        self.identifier += 1
        return self.identifier


users_repository = UsersRepository()


class Weather(object):
    def __init__(self, city='Moscow,ru', lang='en'):
        self._city = city
        self._lang = lang
        self.weather = self.get_weather()

    def get_weather(self):
        from config import WEATHER_APIKEY, WEATHER_URL
        params = {
            'q': self._city,
            'APPID': WEATHER_APIKEY,
            'units': 'metric',
            'lang': self._lang
        }
        _weather = requests.get(WEATHER_URL, params)

        if _weather.status_code == 200:
            _weather = _weather.json()

        conditions, temp, humidity = '', '', ''

        if 'weather' in _weather:
            for data in _weather['weather']:
                conditions = f'{conditions} {data["main"]}, {data["description"]}'
        if 'main' in _weather:
            temp = _weather['main']['temp']
            humidity = _weather['main']['humidity']

        result = (conditions, temp, humidity,)
        return result

    def __dict__(self):
        _weather = self.weather
        _weather_cats = ['conditions', 'temp', 'humidity']
        weather_dict = []
        for index in list(range(len(_weather_cats))):
            weather_dict.append([_weather_cats[index], _weather[index]])

        return dict(weather_dict)

    def __str__(self):
        _weather = self.weather
        weather_str = ''
        for data in _weather:
            weather_str += f'{str(data)} '

        return weather_str


@app.route('/')
@login_required
def index():
    weather = Weather(registeredUser.city, registeredUser.lang)
    return render_template('index.html', user_login=registeredUser.username, weather=str(weather), user_ip=str(registeredUser.ip), user_city=registeredUser.city)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            # todo i'm not sure about this way
            global registeredUser
            registeredUser = users_repository.get_user(username)
            print('Users ' + str(users_repository.users))
            print('Register user %s , password %s' % (registeredUser.username, registeredUser.password))
            if registeredUser != None and registeredUser.password == password:
                print('Logged in..')
                login_user(registeredUser)
                return redirect('/')
            else:
                return abort(401)
        except(AttributeError):
            return abort(401)
    else:
        return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username, password, users_repository.next_index())
        users_repository.save_user(new_user)
        return redirect('/')
    else:
        return render_template('registration.html')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return render_template('index.html', login_fail=True)


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return users_repository.get_user_by_id(userid)


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
