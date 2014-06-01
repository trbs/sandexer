'''
Crawwwwwlinnn in myyyyy skinnnnnnnn
'''
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import urllib
import gzip
import zlib
import StringIO
import bin.utils as utils
from bin.error import Error
import logging


class Crawl():
    def __init__(self, cfg, db, name, url, auth=None, auth_type=None, ua=None, interval=None):
        self._cfg = cfg
        self._db = db
        self.name = name
        self.crawl_url = url
        self.crawl_ua = ua
        self.crawl_auth = auth
        self.crawl_auth_type = HTTPBasicAuth if auth_type == 'basic' else HTTPDigestAuth
        self.crawl_interval = interval
#        self.crawl_ua = ua if ua else cfg.get('Crawler', 'default_ua')
#        self.crawl_interval = interval if interval else cfg.get('Crawler', 'interval')
#        self.pi_name = cfg.get('Protoindex', 'file_name')

    def http(self):
        ua = self.crawl_ua if self.crawl_ua else self._cfg.get('Crawler', 'default_ua')

        try:
            page_root = requests.get(self.crawl_url, verify=False, headers={'User-Agent': ua})
            if not page_root.status_code == 200:
                # Website not found
                return
            else:
                protoindexer = self.fetch_protoindex(self.crawl_url, ua)

                if isinstance(protoindexer, Error):
                    return protoindexer

                if self.verify_protoindex(protoindexer):
                    self.parse_protoindex(protoindexer)

                else:
                    # try for webdav instead
                    return
        except Exception as ex:
            e = Error(ex)
            return e

    def parse_protoindex(self, protoindex):
        pi = protoindex.split('\n')
        data = []
        for line in pi[1:-2]:
            if not line.startswith("f") or line.startswith("d"):
                continue

            spl = line.split(' ')
            file_spl = spl[4].split('/')
            file = file_spl[-1]
            path = '/'.join(file_spl[:-1])
            if not path.endswith('/'): path += '/'

            insertdata = {
                'host_url': self.crawl_url,
                'filetype': line[:1],
                'filesize': spl[2],
                'filepath': urllib.quote_plus(path),
                'filename': urllib.quote_plus(file),
                'filedate': spl[1],
                'filename_clean': '',
                'section': '',
                'imdb': ''
            }

            #self.

    def fetch_protoindex(self, url, ua):
        # download the file in blocks
        read_block_size = 1024*8

        # set up a stream to the file
        page_indexer = requests.get(url + self._cfg.get('Protoindex', 'file_name'),
            stream=True, verify=False, headers={'User-Agent': ua, 'Accept-encoding': 'gzip,deflate'})

        if not page_indexer.status_code == 200:
            return False
        else:
            protoindex_max_size = self._cfg.get('Protoindex', 'file_max_size') * 1048576

            # check server header content-length to determine how big the index file is
            if page_indexer.headers.get('content-length'):
                try:
                    protoindex_size = int(page_indexer.headers['content-length'])

                    if protoindex_size > protoindex_max_size:
                        e = Error('Indexer for \'%s\' exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(protoindex_size)))
                        return e
                except Exception as ex:
                    e = Error(str(ex))
                    return e

            d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file
            protoindex = ''

            while True:
                # read a block
                data = page_indexer.raw.read(read_block_size)

                # terminate if it went over the max file size
                if len(protoindex) > protoindex_max_size:
                    e = Error('Indexer for \'%s\' exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(len(protoindex))))
                    return e

                # break if end of download
                if not data: break

                # decompress and append
                data = d.decompress(data)
                protoindex += data

            return protoindex

    def verify_protoindex(self, protoindex):
        if not protoindex.startswith('# proto-index v=') or not protoindex.endswith('# end proto-index'):
            e = Error('Could not verify index for \'%s\'' % self.name)
            return e
        return True