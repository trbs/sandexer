import sys
import os
import string
import random
from datetime import datetime
import logging
import inspect
from bin.files import Icons

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

def generate_string(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Debug():
    def __init__(self, message, data=None, warning=False, info=False):
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