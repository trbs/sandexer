"""
Manages source objects
"""

from bin.utils import Debug

class Sources():
    def __init__(self, db):
        self.list = []
        self._db = db

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

            self.list.append(source)

class Source():
    def __init__(self, **kwargs):
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