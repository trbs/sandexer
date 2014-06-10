#coding: utf-8
from gevent import monkey
monkey.patch_all()

from bottle import error, post, get, run, static_file, abort, redirect, response, request,  debug, app, route, view, jinja2_view, Jinja2Template

from beaker.middleware import SessionMiddleware
from cork import Cork

import logging

import views.views as Views
import bin.config as config
#from bin.crawler import WebCrawl, FtpCrawl
#from bin.urlparse import ParseUrl
from bin.db import Postgres

cfg = config.Config()
cfg.reload()

if cfg.get('Debug', 'enabled'):
    logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.INFO)
    log = logging.getLogger(__name__)
    debug(True)

cfg = config.Config()
cfg.reload()
db = Postgres(cfg)


# Init bottle app
app = app()

# Use users.json and roles.json in the local users directory
aaa = Cork('users')

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
    return request.forms

def post_get(name, default=''):
    return request.POST.get(name, default).strip()

@route('/')
def root():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    view = Views.Options
    view.important_message = 'Hi welcome to my site please don\'t fucking wreck shit kthx.'
    view.is_admin = request.environ.get('beaker.session')['username'] == 'admin'

    return template('index', login=False, view=view)

@route('/info')
def info():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    view = Views.Options
    view.is_admin = request.environ.get('beaker.session')['username'] == 'admin'

    return template('info', view=view)

@route('/bla')
def info():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    return template('bla')

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
def login():
    return template('login_form', login=False, view=Views.Options(), ascii=True)

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