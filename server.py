#coding: utf-8
import bottle
from bottle import error, post, get, run, static_file, abort, redirect, response, request, template
import views.views as Views
from beaker.middleware import SessionMiddleware
from cork import Cork
import logging

logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)
bottle.debug(True)

# Use users.json and roles.json in the local example_conf directory
aaa = Cork('users', email_sender='federico.ceratto@gmail.com', smtp_url='smtp://smtp.magnet.ie')

app = bottle.app()

session_opts = {
    'session.cookie_expires': True,
    'session.encrypt_key': 'please use a random key and keep it secret!',
    'session.httponly': True,
    'session.timeout': 3600 * 24,  # 1 day
    'session.type': 'cookie',
    'session.validate_key': True,
    }
app = SessionMiddleware(app, session_opts)

def postd():
    return bottle.request.forms


def post_get(name, default=''):
    return bottle.request.POST.get(name, default).strip()

@bottle.route('/')
def root():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    view = Views.Options
    view.important_message = 'Hi welcome to my site please don\'t fucking wreck shit kthx.'
    view.is_admin = bottle.request.environ.get('beaker.session')['username'] == 'admin'

    return template('index', login=False, view=view)

@bottle.route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='static/')

@bottle.route('/login')
def login():
    return template('login_form', login=False, view=Views.Options(), ascii=True)

@bottle.route('/login_post', method='POST')
def login_post():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')

@bottle.route('/user_is_anonymous')
def user_is_anonymous():
    if aaa.user_is_anonymous:
        return 'True'

    return 'False'

@bottle.route('/my_role')
def show_current_user_role():
    """Show current user role"""
    session = bottle.request.environ.get('beaker.session')
    print "Session from simple_webapp", repr(session)
    aaa.require(fail_redirect='/login')
    return aaa.current_user.role

@bottle.route('/admin')
@bottle.view('admin_page')
def admin():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/sorry_page')
    return dict(
        current_user=aaa.current_user,
        users=aaa.list_users(),
        roles=aaa.list_roles()
    )

@bottle.post('/create_user')
def create_user():
    try:
        aaa.create_user(postd().username, postd().role, postd().password)
        return dict(ok=True, msg='')
    except Exception, e:
        return dict(ok=False, msg=e.message)


@bottle.post('/delete_user')
def delete_user():
    try:
        aaa.delete_user(post_get('username'))
        return dict(ok=True, msg='')
    except Exception, e:
        print repr(e)
        return dict(ok=False, msg=e.message)

@bottle.route('/logout')
def logout():
    aaa.logout(success_redirect='/login')

def main():
    bottle.debug(True)
    bottle.run(app=app, host='192.168.178.30', quiet=False, reloader=False)

if __name__ == "__main__":
    main()