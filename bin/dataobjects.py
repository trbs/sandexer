from datetime import datetime

from bin.utils import isInt
from bin.utils import Debug
from urllib import quote_plus, unquote_plus
from bytes2human import human2bytes, bytes2human


class DiscoveredFile():
    def __init__(self, host_name, path, name, isdir, size=None, modified=None, perm=None):
        self.host_name = host_name
        self.filepath = path
        self.filename = name
        self.filesize = int(size) if isInt(size) else size
        self.isdir = isdir
        self.filemodified = modified
        self.fileperm = int(perm) if isInt(perm) else perm

class Sources():
    def __init__(self, db, cfg):
        self.list = []
        self._db = db
        self._cfg = cfg

    def get_sources(self):
        results = self._db.fetch_sources()

        for r in results:
            source = Source()

            source.name = r[0]
            source.added = r[1]
            source.crawl_protocol = r[2]
            source.crawl_username = r[3]
            source.crawl_password = r[4]
            source.crawl_authtype = r[5]
            source.crawl_url = r[6]
            source.crawl_interval = r[7]
            source.crawl_useragent = r[8]
            source.crawl_verifyssl = r[9]
            source.crawl_lastcrawl = r[10]
            source.bandwidth = r[11]
            source.color = r[12]
            source.filetypes = r[13]
            source.description = r[15]
            source.total_size = r[16]
            source.total_files = r[17]
            source.thumbnail_url = r[18] if r[18] else self._cfg.get('General', 'source_default_thumbnail')

            self.list.append(source)


class Source():
    def __init__(self):
        self.name = None
        self.description = None
        self.added = None
        self.crawl_url = None
        self.crawl_protocol = None
        self.crawl_username = None
        self.crawl_password = None
        self.crawl_authtype = None
        self.crawl_interval = None
        self.crawl_useragent = None
        self.crawl_verifyssl = None
        self.crawl_lastcrawl = None
        self.filetypes = []
        self.bandwidth = None
        self.color = None
        self.total_size = 0
        self.total_files = 0
        self.thumbnail_url = None


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

                if isinstance(get_attr, str):
                    tokens = ['filepath', 'filename']
                    if attr in tokens:
                        setattr(dataobject, attr, unquote_plus(get_attr))

        return dataobject