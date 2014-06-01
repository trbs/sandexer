'''
Crawwwwwlinnn in myyyyy skinnnnnnnn
'''
import requests
import gzip
import zlib
import StringIO
import bin.utils as utils
import logging


class Crawl():
    def __init__(self, cfg, name, url, ua=None, interval=None):
        self.cfg = cfg
        self.name = name
        self.crawl_url = url
        self.crawl_ua = ua
        self.crawl_interval = interval
#        self.crawl_ua = ua if ua else cfg.get('Crawler', 'default_ua')
#        self.crawl_interval = interval if interval else cfg.get('Crawler', 'interval')
#        self.pi_name = cfg.get('Protoindex', 'file_name')


    def http(self):
        ua = self.crawl_ua if self.crawl_ua else self.cfg.get('Crawler', 'default_ua')

        try:
            page_root = requests.get(self.crawl_url, headers={'User-Agent': ua})
            if not page_root.status_code == 200:
                # Website not found
                return
            else:
                protoindexer = self.fetch_protoindex(self.crawl_url, ua)

                if protoindexer:
                    self.parse_protoindex(protoindexer)

                else:
                    # try for webdav instead
                    return
        except Exception as e:
            return e

    def parse_protoindex(self, protoindex):
        pi = protoindex.split('\n')

        for line in pi[1:-2]:
            spl = line.split(' ')
            item_type = spl[0]
            item_epoch = spl[1]
            item_size = spl[2]
            item_perm = spl[3]
            item_file = spl[4]
            a = 'e'

    def fetch_protoindex(self, url, ua):
        # download the file in blocks
        read_block_size = 1024*8

        # set up a stream to the file
        page_indexer = requests.get(url + self.cfg.get('Protoindex', 'file_name'),
            stream=True, headers={'User-Agent': ua, 'Accept-encoding': 'gzip,deflate'})

        if not page_indexer.status_code == 200:
            return False
        else:
            protoindex_max_size = self.cfg.get('Protoindex', 'file_max_size') * 1048576

            # check server header content-length to determine how big the index file is
            if page_indexer.headers.get('content-length'):
                protoindex_size = page_indexer.headers['content-length']

                if protoindex_size > protoindex_max_size:
                    logging.fatal('Indexer for \'%s\' exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(protoindex_size)))
                    return False

            d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file
            protoindex = ''

            while True:
                # read a block
                data = page_indexer.raw.read(read_block_size)

                # terminate if it went over the max file size
                if len(protoindex) > protoindex_max_size:
                    logging.fatal('Indexer for \'%s\' exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(len(protoindex))))
                    return False

                # break if end of download
                if not data: break

                # decompress and append
                data = d.decompress(data)
                protoindex += data

            return protoindex if protoindex.startswith('# proto-index v=') else None