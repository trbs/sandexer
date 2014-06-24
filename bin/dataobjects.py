from datetime import datetime

from bin.utils import isInt
from bin.utils import Debug
from urllib import quote_plus, unquote_plus
from bytes2human import human2bytes, bytes2human


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

    def humanize(self, dataobject, humansizes=False, humandates=False, dateformat=None, humanpath=False, humanfile=False):
        for attr in [a for a in dir(dataobject) if not a.startswith('__')]:
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

def UrlVarParse(query):
    parsed = {}

    for key,val in query.iteritems():
        if val.startswith('[') and val.endswith(']'):
            val = val[1:-1]

            if ',' in val:
                val = [z for z in val.split(',') if z]
            else:
                val = [val] if val else None

            if val:
                newval = []

                for v in val:
                    if '=' in v:
                        spl = v.split('=')

                        if len(spl) == 2 and spl[0] and spl[1]:
                            newval.append({spl[0]: spl[1]})

                            continue
                        else:
                            continue

                    newval.append(v)
                parsed[key] = newval

    return parsed

class FlashMessage():
    def __init__(self, key, message, mtype='info'):
        self.key = key
        self.message = message
        self.mtype = mtype