from flask import Flask, Response, redirect, request, abort
from flask_login import LoginManager, UserMixin, \
    login_required, login_user, logout_user

from flask import render_template

app = Flask(__name__)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 5
users = User(0, 'admin', 'password')


# some protected url
@app.route('/')
@login_required
def home():
    return render_template('main.html', user_login=user.name)


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            # if password == username + "_secret":
            # id = username.split('user')[1]
            # global user
            user = User(1, username, password)
            login_user(user)
            return redirect(request.args.get("next"))
        except ():
            return abort(401)
    else:
        return render_template('main.html')


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        password = request.form['password']
        if username != '' and password != '' and password != '':
            global user
            user = User(id, username, password)
            # login_user(user)
            # return redirect(request.args.get("next"))
            return redirect('/login')
        else:
            return abort(401)
    else:
        return render_template('registration.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(id, username, password):
    return User(id, username, password)


if __name__ == "__main__":
    app.run()