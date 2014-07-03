from datetime import datetime
from urllib import quote_plus, unquote_plus
from bin.orm import Source, SourceFile
from bin.utils import Debug

import time

class Cache():
    def __init__(self):
        self._cache_expires = 0  # the amount in seconds at which a cached object is considered expired. if zero, it wont ever expire (unless the source is crawled again)
        self._cache_browse_maxsize = 20
        self._cache_browse_size = 0
        self._cache_browse = {}
        self._cache_search_maxsize = 2
        self._cache_search_size = 0
        self._cache_search = {}

    def browse_lookup(self, source, path):
        if not source in self._cache_browse:
            return False

        if not path in self._cache_browse[source]:
            return False

        cached = self._cache_browse[source][path]

        if 0 < self._cache_expires < self._now() - cached['date']:
            if not cached['precache']:
                del self._cache_browse[source][path]
                self._cache_browse_size -= 1
                return False

        self._cache_browse[source][path]['date'] = self._now()
        return cached

    def browse_insert(self, source, path, files, precache=False):
        if self._cache_browse_size > self._cache_browse_maxsize:
            keys = {}

            for source_k, source_v in self._cache_browse.iteritems():
                for k,v in self._cache_browse[source_k].iteritems():
                    if not v['precache']:
                        keys[v['date']] = dict(source=source_k, path=k)

            oldest = min(keys)
            del self._cache_browse[keys[oldest]['source']][keys[oldest]['path']]
            self._cache_browse_size -= 1

        if not source in self._cache_browse:
            self._cache_browse[source] = {}

        if not path in self._cache_browse[source]:
            self._cache_browse[source][path] = dict(files=files, date=self._now(), precache=precache)
            if not precache: self._cache_browse_size += 1

    def _browse_precache(self, cfg, db, func_prepare):
        Debug('Starting precaching', info=True)

        self.browse_clear()
        sources = db.query(Source).all()

        for source in sources:
            files = db.query(SourceFile).filter(
                SourceFile.source_name == source.name, SourceFile.filepath == '%2F', SourceFile.filename != '/../'
            ).all()

            results = dict(files=files)
            results = func_prepare(cfg, results, source, '/')

            self.browse_insert(
                source=source.name,
                path='/',
                files=results,
                precache=True
            )

            dirs = [z for z in files if z.is_directory and z.filename]

            if dirs:
                Debug('Found %s directories for source \'%s\'' % (str(len(dirs)),source.name), info=True)

            for dir in dirs:
                files = db.query(SourceFile).filter(
                    SourceFile.source_name==source.name,
                    SourceFile.filepath=='%s%s%s' % (dir.filepath, quote_plus(dir.filename), '%2F')
                ).all()

                filepath = '%s%s%s' % (unquote_plus(dir.filepath), dir.filename, '/')
                results = dict(files=files)
                results = func_prepare(cfg, results, source, filepath)

                self.browse_insert(
                    source.name,
                    filepath,
                    results,
                    precache=True
                )

        Debug('Ended precaching', info=True)

    def _now(self):
        return int(time.mktime(datetime.now().timetuple()))

    def browse_clear(self):
        self._cache_browse = {}