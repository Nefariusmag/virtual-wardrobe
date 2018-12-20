from flask import Flask, render_template
from weather import Weather
from users.models import User


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        title = "Your virtual wardrobe"
        user = User()
        weather = Weather(city=user.city, lang=user.lang)
        return render_template('index.html', title=title, weather=weather, user=user)
    return app