from flask import Flask, request, abort, redirect, render_template
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

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
        weather = Weather(current_user.city, current_user.lang)
        return render_template('index.html', user_login=current_user.username, weather=str(weather),
                               user_ip=str(current_user.ip), user_city=current_user.city)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')
        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                registered_user = users_repository.get_user(username)
                print('Users ' + str(users_repository.users))
                print('Register user %s , password %s' % (registered_user.username, registered_user.password))
                if registered_user != None and registered_user.password == password:
                    print('Logged in..')
                    login_user(registered_user)
                    return redirect('/')
                else:
                    return abort(401)
            except(AttributeError):
                return abort(401)
        else:
            return render_template('login.html')

    @app.route('/registration', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect('/')
        # todo add exception if you try to registration user that already exist
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            new_user = User(username, password, users_repository.next_index())
            users_repository.save_user(new_user)
            return redirect('/')
        else:
            return render_template('registration.html')

    @app.route('/location', methods=['GET', 'POST'])
    def change_location():
        if request.method == 'POST':
            city = request.form['city']
            country = request.form['country']
            location = f'{city},{country}'
            current_user.city = location
            return redirect('/')
        else:
            return render_template('location.html')

    # handle login failed
    @app.errorhandler(401)
    def page_not_found(e):
        return render_template('login.html', login_fail=True)

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
    return app
