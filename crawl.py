'''
Crawwwwwlinnn in myyyyy skinnnnnnnn
'''
import requests
import gzip
import zlib
import StringIO


class Crawl():
    def __init__(self):
        self.penis = long
        self.protoindex = '00INDEX.gz'
        self.ua = 'Sanderex WebCrawl'

    def http(self, url, ua=None):
        ua = self.ua if not ua else ua

        try:
            page_root = requests.get(url, headers={'User-Agent': ua})
            if not page_root.status_code == 200:
                # Website not found
                return
            else:
                protoindexer = self.fetch_protoindex(url, ua)

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
        read_block_size = 1024*8

        page_indexer = requests.get(url + self.protoindex,
            stream=True, headers={'User-Agent': ua, 'Accept-encoding': 'gzip,deflate'})

        if not page_indexer.status_code == 200:
            return False
        else:
            d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file
            protoindex = ''

            while True:
                data = page_indexer.raw.read(read_block_size) # read
                if not data: break # break if end of download
                data = d.decompress(data) # decompress
                protoindex += data # append to local data container

            return protoindex if protoindex.startswith('# proto-index v=') else None