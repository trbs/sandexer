"""
    This file is like utils.py, but instead of functions,
    it contains classes I did not know where to put, used
    troughout the program.
"""
from datetime import datetime
from bin.utils import isInt
from urllib import quote_plus, unquote_plus
from bytes2human import human2bytes, bytes2human
import logging
import inspect


class DiscoveredFile():
    def __init__(self, host_name, path, name, isdir, size=None, modified=None, perm=None, fileformat=None, fileext=None, fileadded=None):
        self.host_name = host_name
        self.filepath = path
        self.filename = name
        self.filesize = int(size) if isInt(size) else size
        self.isdir = isdir
        self.filemodified = modified
        self.fileperm = int(perm) if isInt(perm) else perm
        self.fileformat = fileformat
        self.fileext = fileext
        self.fileadded = fileadded
        self.url_icon = None

class DataObjectManipulation():
    def dictionize(self, dataobject):
        d = {}
        for attr in [a for a in dir(dataobject) if not a.startswith('__')]:
            d[attr] = getattr(dataobject, attr)
        return d

    def sanitize(self, dataobject):
        for attr in [a for a in dir(dataobject) if not a.startswith('__') and not a.startswith('_')]:
            get_attr = getattr(dataobject, attr)

            if isinstance(get_attr, str) or isinstance(get_attr, unicode):
                if get_attr == 'None' or get_attr == '':
                    setattr(dataobject, attr, None)
        return dataobject

    def humanize(self, dataobject, humansizes=False, humandates=False, dateformat=None, humanpath=False, humanfile=False):
        for attr in [a for a in dir(dataobject) if not a.startswith('__') and not a.startswith('_')]:
            if humandates:
                get_attr = getattr(dataobject, attr)
                format = '%d %b %Y %H:%M' if not dateformat else dateformat

                if isinstance(get_attr, datetime):
                    setattr(dataobject, attr, get_attr.strftime(format))

            if humansizes:
                get_attr = getattr(dataobject, attr)
                isnum = False

                if isinstance(get_attr, int):
                    isnum = True
                elif isinstance(get_attr, long):
                    isnum = True

                if isnum:
                    tokens = ['filesize', 'bytes', 'total_size']
                    if attr in tokens:
                        setattr(dataobject, attr, bytes2human(get_attr))

            if humanpath or humanfile:
                get_attr = getattr(dataobject, attr)

                if isinstance(get_attr, str) or isinstance(get_attr, unicode):
                    tokens = ['filepath', 'filename']
                    if attr in tokens:
                        setattr(dataobject, attr, unquote_plus(get_attr))

        return dataobject

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

class FlashMessage():
    def __init__(self, key, message, mtype='info'):
        self.key = key
        self.message = message
        self.mtype = mtype