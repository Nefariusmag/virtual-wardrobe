from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Email()])


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('email', validators=[DataRequired(), Email()])

#
# class AddClothes(FlaskForm):
#     from flask_uploads import UploadSet, IMAGES
#     images = UploadSet('images', IMAGES)
#
#     name = StringField
#     clth_type = StringField
#     t_min = StringField
#     t_max = StringField
#     photo = FileField('image', validators=[
#         FileRequired(),
#         FileAllowed(images, 'Images only!')
#     ])
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Email()])


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField('email', validators=[DataRequired(), Email()])

#
# class AddClothes(FlaskForm):
#     from flask_uploads import UploadSet, IMAGES
#     images = UploadSet('images', IMAGES)
#
#     name = StringField
#     clth_type = StringField
#     t_min = StringField
#     t_max = StringField
#     photo = FileField('image', validators=[
#         FileRequired(),
#         FileAllowed(images, 'Images only!')
#     ])
