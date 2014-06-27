from bottle import error, post, get, run, static_file, abort, redirect, response, request, debug, app, route, jinja2_view, Jinja2Template, url, HTTPError, hook, Bottle, jinja2_template
from beaker.middleware import SessionMiddleware

from cork import Cork
import random
import logging
import logging.handlers
import functools, sys, operator
from datetime import datetime
from PIL import Image
import urllib, os

from bin.bytes2human import bytes2human, human2bytes
from bin.files import Icons
from bin.config import Config
from bin.orm import Postgres, Source, SourceFile
from bin.dataobjects import DataObjectManipulation, UrlVarParse, FlashMessage

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from bin.utils import Debug
from bin.api import Api
import bin.forms as Forms

# monkey patch all the things
from gevent import monkey
monkey.patch_all()
from psycogreen.gevent import patch_psycopg
patch_psycopg()

#
@hook('after_request')
def enable_cors():
    response.headers['X-Pirate'] = 'Yarrr'

cfg = Config()
cfg.reload()

logging.basicConfig(format='localhost - - [%(asctime)s] %(message)s', level=logging.DEBUG)
log_handler = logging.handlers.RotatingFileHandler('debug.out', maxBytes=2048576)

log = logging.getLogger('file_logger')
if cfg.get('General', 'debug'):
    log.addHandler(log_handler)
    debug(True)


# Authentication, Authorization and Accounting. Use users.json and roles.json in users/
aaa = Cork('users')

# Init bottle app + database
app = app()
database = Postgres(cfg, app)
app = SessionMiddleware(app, cfg.HttpSessionOptions())
api = Api(cfg)
icons = Icons(cfg)

view = functools.partial(jinja2_view, template_lookup=['templates'])

Jinja2Template.defaults = {
    'url': url,
    'site_name': 'sandexer'
}

Jinja2Template.settings = {
    'autoescape': True,
}

def generate_navigation(admin):
    return [{'href': '/', 'caption': 'Home'},
            {'href': '/browse/', 'caption': 'Browse'},
            {'href': '/search', 'caption': 'Search'},
            {'href': '/logout', 'caption': 'Logout'},
            {'href': '/admin', 'caption': 'Admin'} if admin else None]

def generate_breadcrumps(path, dir='', lastslash=True, capitalize=False):
    crumbs = []
    spl = [z for z in path.split('/') if z]

    for i in range(0,len(spl)):
        link = '/'.join(spl[:i+1])
        if not link.endswith('/'): link += '/'
        name = link[:-1].split('/')[-1]

        crumbs.append({
            'href': dir + link[:-1] if not lastslash else dir + link,
            'name': name.capitalize() if capitalize else name,
            'active': 'active' if i == len(spl) -1 else ''})

    return crumbs

@route('/')
def root():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    message = 'Hi welcome to my site please don\'t fucking wreck shit kthx.'
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    return jinja2_template('index.html',
        title='Home',
        navigation=generate_navigation(admin),
        welcome_message=message
    )

@route('/browse/')
def browse():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    return redirect('/browse?sort=[size=desc]')

@route('/test')
def test(db):
    jinja2_template('bla.html', navigation=generate_navigation(True))

@route('/browse')
def browse(db):
    sort = None
    sort_options = {
        'size': 'total_size',
        'name': 'name',
        'country': 'country',
        'files': 'total_files',
        'bandwidth': 'bandwidth',
        'added': 'added'
    }

    query = UrlVarParse(request.query)

    if 'sort' in query:
        sort = query['sort']
        for s in sort:
            sort_key = None
            sort_val = False
            if isinstance(s, str):
                sort_key = s
            elif isinstance(s, dict):
                sort_key = s.iterkeys().next()
                sort_val = s.itervalues().next()

            if sort_key in sort_options and sort_key:
                sort = {'key': sort_options[sort_key],
                        'val': sort_val}
            else:
                sort = None

    if 'filter' in query:
        filter = query['filter']

    #"""Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    # auth kan met filter db.query(Source).filter_by(name=...)
    sources = db.query(Source).all()

#
#    if sort:
#        sources = sorted(sources, key=lambda k: k.__dict__[sort['key']])
#
#        if sort['val'] == 'desc':
#            sources = sources[::-1]
#    else:
#        sources = sorted(sources, key=lambda k: random.random())

    for source in sources:
        source = DataObjectManipulation().humanize(
            dataobject=source,
            humandates=True, dateformat='%d/%m/%Y %H:%M',
            humansizes=True
        ).calc_filedistribution()

    return jinja2_template('browse_complicated.html',
        title='Browse',
        sources=sources,
        navigation=generate_navigation(True))


@route('/browse/<path:path>')
def browse_dir(path, db):
    #to-do: fix this crap
    start_time = datetime.now()
    files = []
    spl = path.split('/')
    source_name = spl[0]
    source = None
    filepath =  '/' + '/'.join(spl[1:-1])
    filename = ''
    isdir = False

    theme = 'blue'
    theme_path = '/static/icons/%s/128/' % theme

    if path.endswith('/'):
        isdir = True
    else:
        filename = path.split('/')[-1]

    if filepath != '/':
        filepath += '/'

    source = db.query(Source).filter_by(name=source_name).first()

    if source:
        if not isdir:
            get_file = db.query(SourceFile).filter_by(source_name=source_name, filename=filename, filepath=filepath)

            if get_file:
                # file found, redirect to url
                url = source.crawl_url + filepath[1:] + urllib.quote_plus(filename)
                # maybe update some download stats here
                return redirect(url)

        files = db.query(SourceFile).filter_by(source_name=source_name, filepath=urllib.quote_plus(filepath)).all()

        for f in files:
            if f.is_directory:
                if f.filename == '..':
                    f.url_icon = theme_path + icons.additional_icons[20]
                else:
                    f.url_icon = theme_path + icons.additional_icons[21]
                continue

            if f.fileext in icons.additional_icons_exts:
                icon = icons.additional_icons_exts[f.fileext]
                icon = icons.additional_icons[icon]

                f.url_icon = theme_path + icon
            else:
                f.url_icon = theme_path + icons.file_icons[f.fileformat]
        source = source

    def test(k):
        if k.filename == None:
            k.filename = '..'
        else:
            k.filename.lower()
        return k

    files = sorted(files, key=lambda k: test(k).filename)

    dom = DataObjectManipulation()
    for sourcefile in files:
        sourcefile = dom.humanize(sourcefile, humansizes=True, humandates=True, humanfile=True, humanpath=True)

    load_time = (datetime.now() - start_time).total_seconds()

    return jinja2_template('browse_directory.html',
        load_time=load_time,
        title='Browse',
        path=filepath,
        files=files,
        source=source,
        navigation=generate_navigation(admin),
        breadcrumbs=generate_breadcrumps(source_name+filepath, 'browse/')
    )

@route('/search')
def search(db):
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    return jinja2_template('search.html',
        title='Search',
        navigation=generate_navigation(admin)
    )

@route('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='static/')

@route('/login')
def login():
    return jinja2_template('login.html',
        title='Login',
        navigation=[{'href': 'login', 'caption': 'Login'}]
    )

@route('/login_post', method='POST')
def login_post():
    """Authenticate users"""
    username = api.post_get('username')
    password = api.post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')

@route('/post', method='POST')
def post(db):
    #aaa.require(fail_redirect='/404')
    data = request.POST
    result = api.handle_post(db=db, database=database, data=data)

    if isinstance(result, Debug):
        print 'NOOOOOOOOOOOOOO'
        return ';('

    return result

@route('/user_is_anonymous')
def user_is_anonymous():
    if aaa.user_is_anonymous:
        return 'True'

    return 'False'

@route('/my_role')
def show_current_user_role(db):
    """Show current user role"""
    session = request.environ.get('beaker.session')
    print "Session from simple_webapp", repr(session)
    aaa.require(fail_redirect='/login')
    return aaa.current_user.role

@route('/admin/')
def admin():
    aaa.require(role='admin', fail_redirect='/404')
    return redirect('/admin')

@route('/admin')
def admin():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/404')

    return jinja2_template('admin.html',
        title='Admin',
        navigation=generate_navigation(admin=True)
    )


@route('/admin/sources')
def sources(db):
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/404')

    sources = db.query(Source).all()
    dom = DataObjectManipulation()

    for source in sources:
        source = dom.humanize(source, humansizes=True)

    #sources = sorted(sources, key=lambda k: k.name)

    return jinja2_template('sources.html',
        title='Admin',
        navigation=generate_navigation(True),
        sources=sources)

@route('/admin/sources/')
def sources():
    return redirect('/admin/sources')

@route('/admin/sources/delete')
def delete_source():
    aaa.require(role='admin', fail_redirect='/404')
    return redirect('/admin/sources')


@route('/admin/sources/delete/<path:path>', method=['GET', 'POST'])
def delete_source(path, db):
    aaa.require(role='admin', fail_redirect='/404')

    name = path
    source = db.query(Source).filter_by(name=name).first()

    if request.method == 'POST' and source:
        db.delete(source)
        db.execute('DELETE FROM \"files\" WHERE source_name=\'%s\'' % name)
        db.commit()
        return redirect('../')
    else:
        return jinja2_template('source_delete.html',
            source=source,
            name=name,
            navigation=generate_navigation(True),
    )


@route('/admin/sources/edit/<path:path>')
def edit_source(path, db):
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/404')

    name = None
    action = None

    if '/' in path:
        spl = path.split('/')
        name = spl[0]
        action = spl[1]
    else:
        name = path

    source = db.query(Source).filter_by(name=name).first()

    if action:
        if action == 'crawl' and source:
            return jinja2_template('source_crawl.html',
                title='Admin',
                source_name = name,
                path=path,
                navigation=generate_navigation(admin=True),
                breadcrumbs=generate_breadcrumps('/sources/edit/' + name + '/crawl', 'admin/', lastslash=False, capitalize=True)
            )
        else:
            return redirect('/admin/sources')

    return jinja2_template('source_edit.html',
        title='Admin',
        path=path,
        navigation=generate_navigation(admin=True),
        breadcrumbs=generate_breadcrumps('/sources/edit/', 'admin/', lastslash=False, capitalize=True),
        source=source
    )

def verify_upload(upload, dimension=512):
    errors = []
    name, ext = os.path.splitext(upload.filename)

    valid_extensions = ['.jpg', '.png', '.jpeg', '.gif']

    if ext in valid_extensions:
        img=Image.open(upload.file)

        if not img.format in [z[1:].upper() for z in valid_extensions]:
            errors.append(Debug('The upload was not a valid image. Valid extensions are: %s' % ' '.join(valid_extensions)))
        else:
            if img.size[0] > dimension or img.size[1] > dimension:
                errors.append(Debug('Image exceeded dimensions 512x512.'))
            else:
                return {'img': img}
    else:
        errors.append('Extension \'%s\' not allowed. Valid extensions are: %s' % (ext, ' '.join(valid_extensions)))

    return errors

@route('/admin/sources/add', method=['POST', 'GET'])
def source_add(db):
    #"""Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/login')
    errors = [] # dirty hack, watch me care

    form = Forms.sources_add(request.forms)

    if request.method == 'POST':
        validate = form.validate()
        if not validate:
            for k, v in form.errors.iteritems():
                errors.append(FlashMessage(k, v[0], mtype='danger'))
        else:
            i = Source()
            for bu,te in form.data.iteritems():
                setattr(i,bu,te)

            dom = DataObjectManipulation()
            i = dom.sanitize(i)

            upload_errors = []

            if 'thumbnail' in request.files:
                upload = request.files['thumbnail']
                verified = verify_upload(upload)
                if isinstance(verified, dict):
                    name, ext = os.path.splitext(upload.filename)
                    path = 'static/user_upload/icon_%s%s' % (form.data['name'], ext)

                    if not os.path.isdir('static/user_upload'): os.popen('mkdir static/user_upload')
                    if os.path.isfile(path): os.remove(path)

                    verified['img'].save(path)
                    i.thumbnail_url = '/' + path

                elif isinstance(verified, Debug):
                    errors.append(FlashMessage('icon', verified.message, mtype='danger'))
                else:
                    errors.append(FlashMessage('icon', 'unknnown error', mtype='danger'))

            if not errors:
                db.add(i)
                db.commit()
                return redirect('..')

    return jinja2_template('source_add.html',
        form_obj=form._fields,
        title='t',
        navigation=generate_navigation(admin=True),
        form=Forms.sources_add(),
        flashmessages=errors,
        breadcrumbs=generate_breadcrumps('/sources/add', 'admin/', lastslash=False, capitalize=True)
    )

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

@route('/admin/debug')
@view('debug.html')
def debug():
    """Only admins can see this"""
    aaa.require(role='admin', fail_redirect='/404')

    debuglist = []

    try:
        f = open('debug.out', 'r')
        debuglist = f.readlines()
        f.close()
    except:
        pass

    return jinja2_template('debug.html',
        debuglist=reversed(debuglist)
    )

@bottle.error(404)
@bottle.error(405)
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

#import bin.test3

#db.add_source('DebianCD', '')

#
#from bin.urlparse import ParseUrl
#url = ParseUrl('zz')
#
#from datetime import datetime
#from bin.crawler import WebCrawl
#start = datetime.now()
#c = WebCrawl(cfg=cfg, db=db, name='Fluffy', url=url, ua='sandexer webcrawl - dsc - https://github.com/skftn/sandexer/', auth_username='', auth_password='', auth_type='BASIC', crawl_wait=float(0.1))
#aa = c.http()
#from bin.utils import Debug
#if isinstance(aa, Debug):
#    print aa.message
#else:
#    print 'Added: ' + str(aa)
#end = datetime.now()
#print 'TOTAL: ' + str((end - start).total_seconds()) + ' seconds'
#
#c = FtpCrawl(cfg, db, 'hoi', '192.168.178.30', 'ftpuser', 'sda')
#c.ftp()

def main():
    run(app=app, host='192.168.178.30', quiet=True, reloader=False, server='gevent')

if __name__ == "__main__":
    main()