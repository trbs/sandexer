import wtforms as wtf
from wtforms import Form

class RegistrationForm(Form):
    username = wtf.StringField('Username', [wtf.validators.Length(min=4, max=25)])
    email = wtf.StringField('Email Address', [wtf.validators.Length(min=6, max=35)])
    password = wtf.PasswordField('New Password', [
        wtf.validators.DataRequired(),
        wtf.validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = wtf.PasswordField('Repeat Password')
    accept_tos = wtf.BooleanField('I accept the TOS', [wtf.validators.DataRequired()])