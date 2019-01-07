import config
from flask import Flask, request, abort, redirect, render_template
from flask_babel import Babel
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from clothes import Clothes
from wardrobe import db, migrate
from users.models import User
from clothes.models import Clothes
from weather import Weather


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Debug)

    db.init_app(app)
    migrate.init_app(app, db)

    db.create_all(app=app)

    babel = Babel(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    @babel.localeselector
    def get_locale():
        from config import LANGUAGES
        return request.accept_languages.best_match(LANGUAGES)

    @app.route('/')
    @login_required
    def index():
        list_clothes = Clothes.query.filter(Clothes.user_id == current_user.id).all()
        weather = Weather(current_user.geo, current_user.lang)
        return render_template('index.html', user_login=current_user.username, weather=str(weather),
                               user_ip=str(current_user.ip), user_city=current_user.geo, list_clothes=list_clothes,
                               user_id=current_user.id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')
        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                registered_user = User.query.filter(User.username == username).first()
                if registered_user is not None and registered_user.password == password:
                    login_user(registered_user)
                    return redirect('/')
                else:
                    return abort(401)
            except AttributeError:
                return abort(401)
        else:
            return render_template('login.html')

    @app.route('/registration', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect('/')
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            registered_user = User.query.filter(User.username == username).first()
            if registered_user is None:
                new_user = User(username)
                new_user.set_user_password(password)
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            else:
                return render_template('registration.html', user_exit=True)
        else:
            return render_template('registration.html')

    @app.route('/location', methods=['GET', 'POST'])
    def change_location():
        if request.method == 'POST':
            city = request.form['city']
            country = request.form['country']
            location = f'{city},{country}'
            db.session.query(User).filter(User.username == current_user.username).update({'geo': location})
            db.session.commit()
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
        return User.query.get(int(userid))

    # somewhere to logout
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect('/')

    @app.route('/add_clothes', methods=['GET', 'POST'])
    def add_clothes():
        if request.method == 'POST':
            user_id = current_user.id
            clothes_name = request.form['clothes_name']
            type = request.form['type']
            temp_min = request.form['temp_min']
            temp_max = request.form['temp_max']
            if clothes_name == '' or type == '' or temp_max == '' or temp_min == '':
                return render_template('add_clothes.html', add_clothes_fail=True)
            else:
                new_clothes = Clothes(user_id, clothes_name, type, temp_min, temp_max)
                db.session.add(new_clothes)
                db.session.commit()
                return redirect('/add_clothes')
        else:
            return render_template('add_clothes.html')

    return app
