from datetime import datetime
import random
import time

class Cache():
    def __init__(self):
        # the amount in seconds at which a cached object is considered expired
        # if zero, it wont ever expire (unless the source is crawled again)
        self._cache_expires = 0

        # the maximum amount of directories to cache. Not the amount of files.
        self._cache_browse_maxsize = 20

        # dont touch this, its just to keep track
        self._cache_browse_size = 0

        # the cache object
        self._cache_browse = {}

        # same goes for searches
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
            del self._cache_browse[source][path]
            self._cache_browse_size -= 1
            return False
        else:
            self._cache_browse[source][path]['date'] = self._now()
            return cached['files']

    def browse_insert(self, source, path, files):
        if self._cache_browse_size > self._cache_browse_maxsize:
            keys = {}

            for source_k, source_v in self._cache_browse.iteritems():
                for k,v in self._cache_browse[source_k].iteritems():
                    keys[v['date']] = dict(source=source_k, path=k)

            oldest = min(keys)
            del self._cache_browse[keys[oldest]['source']][keys[oldest]['path']]
            self._cache_browse_size -= 1

        if not source in self._cache_browse:
            self._cache_browse[source] = {}

        if not path in self._cache_browse[source]:
            self._cache_browse[source][path] = dict(files=files, date=self._now())
            self._cache_browse_size += 1

    def _now(self):
        return int(time.mktime(datetime.now().timetuple()))

    def browse_clear(self):
        self._cache_browse = {}