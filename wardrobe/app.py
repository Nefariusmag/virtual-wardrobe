from flask import Flask, request, abort, redirect, render_template
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_babel import Babel, _

from users.models import User, UsersRepository
from weather import Weather


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'

    babel = Babel(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    users_repository = UsersRepository()

    @babel.localeselector
    def get_locale():
        from config import LANGUAGES
        return request.accept_languages.best_match(LANGUAGES)

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
                if registeredUser != None and registeredUser.password == password:
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
    return app