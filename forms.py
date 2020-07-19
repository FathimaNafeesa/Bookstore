from wtforms import Form,StringField,TextAreaField,PasswordField,validators,SubmitField
from flask_wtf import FlaskForm

class RegisterForm(FlaskForm):
    username = StringField('username', [validators.Length(min=4, max=25)])
    email = StringField('email', [validators.Length(min=6, max=50)])
    phone = StringField('phone',[validators.Length(min=7,max=15)])
    password = PasswordField('password', [
        validators.Length(min=2, max=50),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('confirm')
    submit = SubmitField('Sign Up')

class ActivationForm(FlaskForm):
    otp = StringField('otp',[validators.Length(min=3, max=7)])
    phone = StringField('phone',[validators.Length(min=3, max=15)])
    submit = SubmitField('check otp')

class LoginForm(Form):
    username = StringField('username', [validators.Length(min=4, max=25)])
    password = PasswordField('password', [validators.Length(min=8, max=50)])