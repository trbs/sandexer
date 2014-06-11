from gevent import monkey
monkey.patch_all()

from bottle import error, post, get, run, static_file, abort, redirect, response, request,  debug, app, route, jinja2_view, Jinja2Template, url

from beaker.middleware import SessionMiddleware
from cork import Cork

import logging
import functools

from bin.config import Config
from bin.db import Postgres
from bin.utils import Debug

cfg = Config()
cfg.reload()

if cfg.get('General', 'debug'):
    logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.INFO)
    log = logging.getLogger(__name__)
    debug(True)

# Init DB
db = Postgres(cfg)
db.init_db()
db.add_source('hoi', '')

# Authentication, Authorization and Accounting. Use users.json and roles.json in users/
aaa = Cork('users')

# Init bottle app
app = SessionMiddleware(app(), cfg.HttpSessionOptions())

# Wrapping jinja2_view for easier access
view = functools.partial(jinja2_view, template_lookup=['templates'])

Jinja2Template.defaults = {
    'url': url,
    'site_name': 'sandexer'
}
Jinja2Template.settings = {
    'autoescape': True,
}

def postd():
    return request.forms

def post_get(name, default=''):
    return request.POST.get(name, default).strip()

def generate_navigation(admin):
    return [{'href': '/', 'caption': 'Home'},
            {'href': '/browse', 'caption': 'Browse'},
            {'href': '/search', 'caption': 'Search'},
            {'href': '/logout', 'caption': 'Logout'},
            {'href': '/admin', 'caption': 'Admin'} if admin else None]

@route('/')
@view('index.html')
def root():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    message = 'Hi welcome to my site please don\'t fucking wreck shit kthx.'
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    return {
        'title': 'Home',
        'navigation': generate_navigation(admin),
        'welcome_message': message
    }

@route('/debug')
@view('debug.html')
def info():
    """Only admins can see this"""
    aaa.require(role='admin', fail_redirect='/404')

    return {
        ''
    }

@route('/bla/:name', name='bla')
@view('bla.html')
def info(name):
    """Only authenticated users can see this"""
    #aaa.require(fail_redirect='/login')

    return {'name': name, 'title': 'hoi'}

@route('/search')
def search():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    view = Views.Options
    view.is_admin = request.environ.get('beaker.session')['username'] == 'admin'

    return template('search', view=view)

@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='static/')

@route('/login')
@view('login.html')
def login():
    return {
        'title': 'Login',
        'navigation': [{'href': 'login', 'caption': 'Login'}]
    }

@route('/login_post', method='POST')
def login_post():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')

@route('/post', method='POST')
def post():
    aaa.require(fail_redirect='/login')
    name = post_get('name')
    a = request.POST
    print name

@route('/user_is_anonymous')
def user_is_anonymous():
    if aaa.user_is_anonymous:
        return 'True'

    return 'False'

@route('/my_role')
def show_current_user_role():
    """Show current user role"""
    session = request.environ.get('beaker.session')
    print "Session from simple_webapp", repr(session)
    aaa.require(fail_redirect='/login')
    return aaa.current_user.role

@route('/admin')
@view('admin')
def admin():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/sorry_page')

    view = Views.Options()
    view.is_admin = request.environ.get('beaker.session')['username'] == 'admin'

    return dict(
        current_user=aaa.current_user,
        users=aaa.list_users(),
        roles=aaa.list_roles(),
        view=view
    )

@route('/admin/sources')
def sources():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/login')

    return template('sources')

@route('/admin/sources/add')
def source_add():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/login')

    return template('source_add')
import bottle
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

@route('/logout')
def logout():
    aaa.logout(success_redirect='/login')

@bottle.error(404)
@bottle.error(500)
@bottle.error(501)
@bottle.error(502)
@bottle.error(503)
@bottle.error(504)
@bottle.error(505)
@view('error.html')
def error404(error):
    return {
        'title': 'Error'
    }

#
#url = ParseUrl('http://192.168.178.30/files/')

#import bin.test

from datetime import datetime
#start = datetime.now()
#c = WebCrawl(cfg, db, 'WipKip', url, ua='sandexer webcrawl - Kusjes van dsc - https://github.com/skftn/sandexer/')
#aa = c.http()
#from bin.utils import Debug
#if isinstance(aa, Debug):
#    print aa.message
#else:
#    print 'Added: ' + str(aa)
#end = datetime.now()
#print 'TOTAL: ' + str((end - start).total_seconds()) + ' seconds'

#c = FtpCrawl(cfg, db, 'hoi', '192.168.178.30', 'ftpuser', 'sda')
#c.ftp()

def main():
    run(app=app, host='192.168.178.30', quiet=False, reloader=False, server='gevent')

if __name__ == "__main__":
    main()