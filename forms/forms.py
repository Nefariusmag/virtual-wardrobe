from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(min=0, max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=0, max=80)],render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(min=0, max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=0, max=80)],render_kw={"placeholder": "Password"})
