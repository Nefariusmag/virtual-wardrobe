import os, config, datetime

from flask import Flask, abort, render_template, request, redirect, url_for, send_from_directory
from flask_babel import Babel
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from wardrobe import db, migrate, InitDefaults
from rest import WardrobeAPI as WAPI
from users.models import User, UserRole
from clothes.models import Clothes
from weather import Weather
from config import upload_folder, allowed_extensions


# TODO change this shit on some color sort
def get_list_look(color, current_user_id):
    if color == 'red':
        list_color_type_clothes = Clothes.query.filter(Clothes.user_id == current_user_id) \
            .filter(Clothes.color_blue <= 140) \
            .filter(Clothes.color_red >= 120) \
            .filter(Clothes.color_green <= 120).all()
    if color == 'green':
        list_color_type_clothes = Clothes.query.filter(Clothes.user_id == current_user_id) \
            .filter(Clothes.color_blue <= 120) \
            .filter(Clothes.color_red <= 120) \
            .filter(Clothes.color_green >= 140).all()
    if color == 'blue':
        list_color_type_clothes = Clothes.query.filter(Clothes.user_id == current_user_id) \
            .filter(Clothes.color_blue >= 140) \
            .filter(Clothes.color_red <= 120) \
            .filter(Clothes.color_green <= 130).all()

    return list_color_type_clothes


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Default)

    db.init_app(app)
    migrate.init_app(app, db)

    db.create_all(app=app)

    with app.app_context():
        initd = InitDefaults(('import_default_clothe_types', app.root_path),
                             ('import_default_user_roles', ('admin', 'service', 'user')))
        initd()

    babel = Babel(app)

    login_manager = LoginManager()
    login_manager.login_view = "login"
    login_manager.init_app(app)

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = upload_folder
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions

    @app.route('/api/<version>/<apicmd>', methods=['GET', 'POST'])
    def api(version='', apicmd=''):
        args = (request.args, request.headers, request.get_json(force=True, silent=True))
        kw_api_args = {'v': version, 'apicmd': apicmd, 'method': request.method}
        return WAPI(db, *args, **kw_api_args).response

    @app.route('/', methods=['GET', 'POST'])
    @login_required
    def index():
        weather = Weather(current_user.geo, current_user.lang)

        temperature = weather.temp
        list_clothes = Clothes.query.filter(Clothes.user_id == current_user.id).filter(
            Clothes.temperature_min <= temperature).filter(Clothes.temperature_max >= temperature).all()

        if request.method == "POST" and request.form['type_look'] != 'all':
            list_clothes = get_list_look(request.form['type_look'], current_user.id)

        list_clth_types = Clothes.Types.query.filter(Clothes.Types.id.in_([int(i.clth_type) for i in list_clothes])).all()

        return render_template('index.html', user_login=current_user.username, weather=str(weather),
                               user_ip=str(current_user.ip), user_city=current_user.geo, user_id=current_user.id,
                               list_clothes=list_clothes, list_clth_types=list_clth_types)

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
                new_user.role = db.session.query(UserRole.id).filter(UserRole.role == 'user').first().id
                db.session.add(new_user)
                db.session.commit()
                db.session.add(new_user.UserToken(user_id=new_user.id))
                db.session.add(new_user.UserToken(user_id=new_user.id, token_type='totp'))
                db.session.commit()
                return redirect('/')
            else:
                return render_template('registration.html', user_exit=True)
        else:
            return render_template('registration.html')

    @app.route('/location', methods=['GET', 'POST'])
    @login_required
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
    @login_required
    def add_clothes():
        if request.method == 'POST':
            user_id = current_user.id
            clothes_name = request.form['clothes_name']
            type = Clothes.Types.query.filter(Clothes.Types.desc == request.form['type']).first().id
            temp_min = int(request.form['temp_min'])
            temp_max = int(request.form['temp_max'])
            photo_file = getattr(request.files, 'photo', 0)
            try:
                photo_file = request.files['photo']
                if allowed_file(photo_file.filename):
                    filename = f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")}.jpg'
                    photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except:
                filename = ''
            if clothes_name and type and temp_max and temp_min and temp_max >= temp_min:
                new_clothes = Clothes(user_id, clothes_name, type, temp_min, temp_max, filename)
                db.session.add(new_clothes)
                db.session.commit()
                return redirect('/add_clothes')
            else:
                return render_template('add_clothes.html', add_clothes_fail=True)
        else:
            return render_template('add_clothes.html')

    return app
