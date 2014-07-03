from bottle import error, post, get, run, static_file, abort, redirect, response, request, debug, app, route, jinja2_view, Jinja2Template, url, HTTPError, hook, Bottle, jinja2_template
from beaker.middleware import SessionMiddleware

from cork import Cork
import random
import logging
import logging.handlers
import functools, sys, operator
from datetime import datetime
from PIL import Image
from urllib import quote_plus, unquote_plus
import os

from bin.bytes2human import bytes2human
from bin.config import Config
from bin.orm import Postgres, Source, SourceFile, or_
from bin.dataobjects import DataObjectManipulation, FlashMessage
from bin.utils import Debug, set_icon, sort_alpha_keygetter, gen_action_fetches, gen_navigation, gen_breadcrumps, verify_upload, var_parse
from bin.api import Api
import bin.forms as Forms
from bin.cache import Cache

# monkey patch all the things
from gevent import monkey
monkey.patch_all()
from psycogreen.gevent import patch_psycopg
patch_psycopg()

# hook like a true pirate
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
cache = Cache()

#view = functools.partial(jinja2_view, template_lookup=['templates'])

Jinja2Template.defaults = {
    'url': url,
    'site_name': 'sandexer'
}

Jinja2Template.settings = {
    'autoescape': True,
}

@route('/')
def root():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    message = 'Not done yet.'
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    return jinja2_template('index.html',
        title='Home',
        navigation=gen_navigation(admin),
        welcome_message=message
    )

@route('/browse/')
def browse():
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')

    return redirect('/browse?sort=[size=desc]')

@route('/test')
def test(db):
    files = db.query(SourceFile).filter(SourceFile.filename.like('%python%'), SourceFile.source_name=='aceton', SourceFile.is_directory==False).all()
    import random
    ran = str(random.randrange(3,39))

    r = cache.browse_lookup('aceton', '%2Fmusic%2F')
    if not r:
        cache.browse_insert('aceton', '%2Fmusic%2F', files)
    else:
        e = 'e'
    return ''

@route('/browse')
def browse(db):
    #"""Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    sort = None
    sort_options = {
        'size': 'total_size',
        'name': 'name',
        'country': 'country',
        'files': 'total_files',
        'bandwidth': 'bandwidth',
        'added': 'added'
    }

    query = var_parse(request.query)

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

    sources = db.query(Source).all()

    for source in sources:
        source = DataObjectManipulation().humanize(
            dataobject=source,
            humandates=True, dateformat='%d/%m/%Y %H:%M',
            humansizes=True
        ).calc_filedistribution()

    sources = [z for z in sources if z.crawl_protocol == 'HTTP(s)']

    return jinja2_template('browse_complicated.html',
        title='Browse',
        sources=sources,
        navigation=gen_navigation(admin))

@route('/browse/<path:path>')
def browse_dir(path, db):
    #"""Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    filename = ''
    isdir = False

    spl = path.split('/')
    source_name = spl[0]
    filepath =  '/' + '/'.join(spl[1:-1])

    if path.endswith('/'):
        isdir = True
    else:
        filename = path.split('/')[-1]

    if filepath != '/':
        filepath += '/'

    start_dbtime = datetime.now()
    source = db.query(Source).filter_by(name=source_name).first()
    results = {}

    if source:
        if not isdir:
            get_file = db.query(SourceFile).filter_by(source_name=source_name, filename=filename, filepath=filepath)

            if get_file:
                # file found, redirect to url
                url = source.crawl_url + filepath + quote_plus(filename)
                # maybe update some download stats here
                return redirect(url)

    in_cache = cache.browse_lookup(source_name, filepath)

    if not in_cache:
        results['files'] = db.query(SourceFile).filter_by(source_name=source_name,
            filepath=
            quote_plus(filepath)
        ).all()

        # set icons
        results['files'] = set_icon(cfg, results['files'])

        # sort alphabetically
        results['files'] = sorted(results['files'], key=lambda k: sort_alpha_keygetter(k).filename)

        # folders always on top would be nice too
        results['files'] = sorted(results['files'], key=lambda k: sort_alpha_keygetter(k).is_directory, reverse=True)

        total_size_files = 0
        dom = DataObjectManipulation()
        for file in results['files']:
            total_size_files += file.filesize
            file = dom.humanize(file, humansizes=True, humandates=True, humanfile=True, humanpath=True)

        results['total_size_files'] = bytes2human(total_size_files)
        cache.browse_insert(source_name, filepath, results)
    else:
        results = in_cache

    load_time = (datetime.now() - start_dbtime).total_seconds()

    return jinja2_template('browse_directory.html',
        load_time=load_time,
        title='Browse',
        path=filepath,
        fetch=gen_action_fetches(source, filepath),
        path_quoted=quote_plus(filepath),
        files_size=results['total_size_files'],
        files=results['files'],
        source=source,
        navigation=gen_navigation(admin),
        breadcrumbs=gen_breadcrumps(source_name+filepath, 'browse/')
    )

@route('/search')
def search(db):
    """Only authenticated users can see this"""
    aaa.require(fail_redirect='/login')
    admin = request.environ.get('beaker.session')['username'] == 'admin'

    vars = var_parse(request.query)
    errors = []

    if 'query' in vars:
        if not len(vars['query']) >= 0:
            errors.append(FlashMessage('Search', 'String must contain 3 characters or more', mtype="warning"))
        else:
            max_results = 200
            start = datetime.now()

            # build the query
            q = db.query(SourceFile)

            if 'server' in vars:
                servers = vars['server']

                if isinstance(servers, list):
                    opor = or_()

                    for server in servers:
                        if 3 <= len(server) <= 14:
                            opor.append(SourceFile.source_name == server)

                    q = q.filter(opor)

            if 'extension' in vars:
                exts = vars['extension']

                if isinstance(vars['extension'], list):
                    opor = or_()

                    for ext in exts:
                        if 1 <= len(ext) <= 10:
                            opor.append(SourceFile.fileext == ext)

                    q = q.filter(opor)

            if 'category' in vars:
                cats = vars['category']

                if isinstance(cats, list):
                    if not 'all' in cats:
                        opor = or_()

                        categories = {
                            'all': 0,
                            'documents': 1,
                            'movies': 2,
                            'music': 3,
                            'pictures': 4
                        }

                        for cat in cats:
                            if cat in categories:
                                opor.append(SourceFile.fileformat == categories[cat])

                        q = q.filter(opor)

            if 'path' in vars:
                path = vars['path']

                if isinstance(path, str):
                    if len(path) > 3:
                        path = quote_plus(path).lower()
                        q = q.filter(SourceFile.filepath_low.like(path+'%'))

            # fetch results
            search_query = quote_plus(vars['query']).lower()
            q = q.filter(SourceFile.filename_low.like('%'+search_query+'%'))
            results = q.all()

            load_time = (datetime.now() - start).total_seconds()

            num_results = len(results)
            results = results[:max_results]

            # humanize filesizes
            dom = DataObjectManipulation()
            for f in results:
                f = dom.humanize(f, humansizes=True, humanpath=True)

            # set icons
            results = set_icon(cfg, results)

            # sort alphabetically
            results = sorted(results, key=lambda k: sort_alpha_keygetter(k).filename)

            # folders always on top would be nice too
            results = sorted(results, key=lambda k: sort_alpha_keygetter(k).is_directory, reverse=True)

            db.rollback()

            sources_list = db.query(Source).all()
            sources_dict = {}
            for source in sources_list:
                sources_dict[source.name] = source

            return jinja2_template('search_results.html',
                files=results,
                query=vars,
                sources=sources_dict,
                num_results=num_results,
                load_time=load_time,
                navigation=gen_navigation(admin)
            )

    return jinja2_template('search.html',
        title='Search',
        navigation=gen_navigation(admin),
        flashmessages=errors
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
        navigation=gen_navigation(admin=True)
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
        navigation=gen_navigation(True),
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
            navigation=gen_navigation(True),
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
                navigation=gen_navigation(admin=True),
                breadcrumbs=gen_breadcrumps('/sources/edit/' + name + '/crawl', 'admin/', lastslash=False, capitalize=True)
            )
        else:
            return redirect('/admin/sources')

    return jinja2_template('source_edit.html',
        title='Admin',
        path=path,
        navigation=gen_navigation(admin=True),
        breadcrumbs=gen_breadcrumps('/sources/edit/', 'admin/', lastslash=False, capitalize=True),
        source=source
    )

@route('/admin/sources/add', method=['POST', 'GET'])
def source_add(db):
    #"""Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/login')
    errors = []

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

                    if not os.path.isdir('static/user_upload'):
                        os.popen('mkdir static/user_upload')
                    if os.path.isfile(path):
                        os.remove(path)

                    try:
                        save_path = 'static/user_upload/icon_%s.png' % form.data['name']
                        verified['img'].save(save_path)
                        i.thumbnail_url = '/' + save_path
                    except Exception as e:
                        errors.append(FlashMessage('icon', 'unknown error, pick another image', mtype='danger'))

                elif isinstance(verified, Debug):
                    errors.append(FlashMessage('icon', verified.message, mtype='danger'))
                else:
                    errors.append(FlashMessage('icon', 'unknown error, pick another image', mtype='danger'))

            if not errors:
                db.add(i)
                db.commit()
                return redirect('..')

    return jinja2_template('source_add.html',
        form_obj=form._fields,
        title='t',
        navigation=gen_navigation(admin=True),
        form=Forms.sources_add(),
        flashmessages=errors,
        breadcrumbs=gen_breadcrumps('/sources/add', 'admin/', lastslash=False, capitalize=True)
    )

import bottle
@route('/create_user')
def create_user():
    aaa.require(role='admin', fail_redirect='/login')
    try:
        aaa.create_user('user', 'user', 'hiephoi', 'admin@admin.com', description='The admin yo')
        #aaa.create_user(postd().username, postd().role, postd().password)
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
def error404(error):
    return jinja2_template('error.html',
        title='Error'
    )

#c = FtpCrawl(cfg, db, 'hoi', '', '', '')
#c.ftp()

def main():
    run(app=app, host='192.168.178.30', quiet=False, reloader=False, server='gevent')

if __name__ == "__main__":
    main()