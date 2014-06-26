import wtforms as wtf
from wtforms import Form
from bin.config import Config

CONFIG = Config()
CONFIG.reload()

class RegistrationForm(Form):
    username = wtf.StringField('Username', [wtf.validators.Length(min=4, max=25)])
    email = wtf.StringField('Email Address', [wtf.validators.Length(min=6, max=35)])
    password = wtf.PasswordField('New Password', [
        wtf.validators.DataRequired(),
        wtf.validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = wtf.PasswordField('Repeat Password')
    accept_tos = wtf.BooleanField('I accept the TOS', [wtf.validators.DataRequired()])

def validate_protocol(form, field):
    protocols = ['HTTP(s)', 'FTP', 'SMB', 'LOCAL']
    if not field.data in protocols:
        raise wtf.ValidationError('Protocol \'%s\' is not known.' % field.data)

def validate_crawlinterval(form, field):
    pass

def validate_authtype(form, field):
    pass

def validate_crawlua(form, field):
    pass

def validate_crawlwait(form, field):
    pass


class sources_add(Form):
    name = wtf.StringField('Name', [
        wtf.validators.Length(min=3, max=14),
        wtf.validators.DataRequired(),
        wtf.validators.regexp('^\w+$', message="Alphanummeric and underscores only (a-b A-B 0-9 _)")
    ])

    crawl_protocol = wtf.SelectField('Protocol', choices=[('HTTP(s)', "HTTP(s)"), ('FTP', "FTP"), ('SMB', 'SMB'), ('LOCAL', 'LOCAL')], default=1, validators=[wtf.validators.DataRequired(), validate_protocol])

    crawl_url = wtf.StringField('Location',
        validators=[wtf.validators.DataRequired()]
    )

    crawl_username = wtf.StringField('Username')
    crawl_password = wtf.StringField('Password')
    crawl_authtype = wtf.SelectField('Type', choices=[('None', 'None'), ('HTTP_BASIC', "HTTP(s) BASIC"), ('HTTP_DIGEST', "HTTP(s) DIGEST")], default=1, validators=[validate_authtype])

    crawl_interval = wtf.SelectField('Interval', choices=[('None', 'None'), ('1 hour', 'Every hour'), ('2 hours', 'Every 2 hours') ,('4 hours', 'Every 4 hours'), ('12 hours', "Every 12 hours"), ('24 hours', "Every 24 hours"), ('2 days', 'Every 2 days'), ('5 days', 'Every 5 days'),('weekly', 'Every week'), ('2 weeks', 'Every 2 weeks'), ('monthly', 'Every month')], default=1, validators=[validate_crawlinterval])

    crawl_wait = wtf.SelectField('Wait', choices=[('None', 'None'), ('50', '50 ms'), ('100', '100 ms'), ('150', '150 ms'), ('200', '200 ms'), ('250', '250 ms'), ('300', '300 ms')], default=1, validators=[validate_crawlwait])

    crawl_useragent = wtf.StringField('User-Agent', default=CONFIG.get('Crawler', 'default_ua'), validators=[validate_crawlua])

    crawl_verifyssl = wtf.BooleanField('Verify SSL', default=False)

    bandwidth = wtf.StringField('Bandwidth', [wtf.validators.length(min=0, max=4)])

    country = wtf.SelectField('Country', choices=[('None', 'Empty'), ('nl', 'nl')], default=1)

    description = wtf.StringField('Description', [wtf.validators.length(min=0, max=360)])

    thumbnail = wtf.FileField('Image')

