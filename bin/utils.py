import sys
import os
import string
import random
from datetime import datetime
import logging
import inspect
from bin.files import Icons
from PIL import Image

def bytesTo(bytes, to, bsize=1024):
    r = float(bytes)
    for i in range({'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }[to]):
        r = r / bsize
    return(r)

def isInt(num):
    try:
        a = int(num)
        return True
    except:
        return False

def gen_string(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Debug():
    def __init__(self, message, data=None, warning=False, info=False, broadcast=True):
        try:
            self.caller = inspect.stack()[1][0].f_locals.get('self', None).__class__.__name__
        except:
            self.caller = '?'

        self._log = logging.getLogger('file_logger')
        self.now = datetime.now()
        self.message = message
        self.data = data

        msg = 'class:%s:{{TYPE}} - %s' % (self.caller,message)
        date = self.now.strftime('%d %b %Y %H:%M:%S')

        if broadcast:
            if warning:
                self._log.warning('%s:%s' % (date,msg.replace('{{TYPE}}', 'WARNING')))
            elif info:
                self._log.info('%s:%s' % (date,msg.replace('{{TYPE}}', 'INFO')))
            else:
                self._log.error('%s:%s' % (date,msg.replace('{{TYPE}}', 'ERROR')))


def set_icon(cfg, files):
    icons = Icons(cfg)

    theme = 'blue'
    theme_path = '/static/icons/%s/128/' % theme

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

    return files

def sort_alpha_keygetter(k):
    if k.filename == None:
        k.filename = '..'
    else:
        k.filename.lower()
    return k

def gen_action_fetches(source, path):
    url = source.crawl_url
    if path == '/':
        path = ''
    elif path.startswith('/') and url.endswith('/'):
        path = path[1:]

    wget_extras = ''
    lftp_extras = ''
    if source.crawl_authtype:
        wget_extras = 'user=%s password=%s ' % (source.crawl_username, source.crawl_password)

        if source.crawl_authtype == 'HTTP_DIGEST':
            lftp_extras = Debug('Authentication using DIGEST is not supported by lftp')
        else:
            lftp_extras = '-u %s,%s ' % (source.crawl_username, source.crawl_password)

    wget = 'wget %s-r -nH --no-parent \'%s\'' % (wget_extras, url + path)

    if not isinstance(lftp_extras, Debug):
        lftp = 'lftp %s-e \'mirror\' %s' % (lftp_extras, url+path)
    else:
        lftp = lftp_extras.message

    return dict(wget=wget,lftp=lftp)

def gen_navigation(admin):
    return [{'href': '/', 'caption': 'Home'},
            {'href': '/browse/', 'caption': 'Browse'},
            {'href': '/search', 'caption': 'Search'},
            {'href': '/logout', 'caption': 'Logout'},
            {'href': '/admin', 'caption': 'Admin'} if admin else None]

def gen_breadcrumps(path, dir='', lastslash=True, capitalize=False):
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

def verify_upload(upload, dimension=512):
    errors = []
    name, ext = os.path.splitext(upload.filename)

    valid_extensions = ['.jpg', '.png', '.jpeg', '.gif']

    if ext in valid_extensions:
        img = None
        try:
            img=Image.open(upload.file)
        except Exception as e:
            errors.append(Debug(str(e)))

        if img and not img.format in [z[1:].upper() for z in valid_extensions]:
            errors.append(Debug('The upload was not a valid image. Valid extensions are: %s' % ' '.join(valid_extensions)))
        elif img:
            if img.size[0] > dimension or img.size[1] > dimension:
                errors.append(Debug('Image exceeded dimensions 512x512.'))
            else:
                return {'img': img}
    else:
        errors.append('Extension \'%s\' not allowed. Valid extensions are: %s' % (ext, ' '.join(valid_extensions)))

    return errors