from flask import Flask, request, abort, redirect, render_template
from flask_login import LoginManager, login_required, login_user, logout_user

from users.models import User, UsersRepository
from weather import Weather


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    users_repository = UsersRepository()

    @app.route('/')
    @login_required
    def index():
        weather = Weather(registeredUser.city, registeredUser.lang)
        return render_template('index.html', user_login=registeredUser.username, weather=str(weather),
                               user_ip=str(registeredUser.ip), user_city=registeredUser.city)

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
        # todo add exception if you try to registration user that already exist
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            new_user = User(username, password, users_repository.next_index())
            users_repository.save_user(new_user)
            return redirect('/login')
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

    @app.route('/add_clothes', methods=['GET', 'POST'])
    def add_clothes():
        if request.method == 'POST':
            print(registeredUser.username)
            user = users_repository.get_id_by_user(registeredUser.username)
            user_id = user.uid
            clothes_name = request.form['clothes_name']
            type = request.form['type']
            temp_min = request.form['temp_min']
            temp_max = request.form['temp_max']
            if clothes_name == '' or type == '' or temp_max == '' or temp_min == '':
                return render_template('add_clothes.html', add_clothes_fail=True)
            else:
                print(f'{user_id}, {clothes_name}, {type}, {temp_min}, {temp_max}')
                # new_clothes = Clothes(username_id, clothes_name, type, top, bottom, upper, lower, temp_min, temp_max)
                return redirect('/add_clothes')
        else:
            return render_template('add_clothes.html')

    return app
