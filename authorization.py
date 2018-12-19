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

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.username, key='secret_key')


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


@app.route('/')
@login_required
def index():
    return render_template('index.html', user_login=registeredUser.username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
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
