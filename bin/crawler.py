'''
Crawwwwwlinnn in myyyyy skinnnnnnnn
'''
from gevent import monkey; monkey.patch_all()
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import zlib
from mongo import DiscoveredFile
from bin.utils import isInt
from bin.error import Error

# to-do:
# clean up some exceptions
# requests timeout

class WebCrawl():
    def __init__(self, cfg, db, name, url, auth_username=None, auth_password=None, auth_type=None, ua=None, ssl_verify=False, interval=None):
        self._cfg = cfg
        self._db = db
        self.name = name
        self.crawl_url = url
        self.crawl_ua = ua if ua else self._cfg.get('Crawler', 'default_ua')
        self.crawl_sslverify = ssl_verify
        self.crawl_auth_type = HTTPBasicAuth if auth_type == 'BASIC' else HTTPDigestAuth
        self.crawl_auth = None if not auth_type else self.crawl_auth_type(auth_username, auth_password)
        self.crawl_interval = interval

    def http(self):
        try:
            url_head = requests.head(self.crawl_url,
                verify=self.crawl_sslverify,
                auth=self.crawl_auth,
                headers={'User-Agent': self.crawl_ua})

            if not url_head.status_code == 200:
                # Website not found
                return
            else:
                discovered_files = None

                # try fetching protoindexer
                protoindexer = self.fetch_protoindex(self.crawl_url, self.crawl_ua)

                if isinstance(protoindexer, Error):
                    pass
                else:
                    verify = self.verify_protoindex(protoindexer)

                    # if the indexer verification fails it'll fall back to opendir crawling
                    if not isinstance(verify, Error):
                        discovered_files = self.parse_protoindex(protoindexer)

                if not discovered_files:
                    # go for opendir
                    discovered_files = self.parse_opendir()

                if isinstance(discovered_files, Error):
                    # if that also fails, quit trying
                    return discovered_files

                if len(discovered_files) == 0:
                    return 0
                else:
                    return self._db.try_add_files(discovered_files)

        except Exception as ex:
            return Error(ex)

    def parse_protoindex(self, protoindex):
        # needs try catch block
        pi = protoindex.split('\n')
        data = []

        try:
            for line in pi[1:-2]:
                if not line.startswith("f") and not line.startswith("d"):
                    continue

                spl = line.split(' ')
                filetype = line[:1]
                path = ''

                if filetype == 'f':
                    file_spl = spl[4].split('/')
                    file = file_spl[-1]
                    path = '/'.join(file_spl[:-1])
                    if not path.endswith('/') and path != '': path += '/'
                else:
                    if not spl[4] != '':
                        path = spl[4] if spl[4].endswith('/') else spl[4] + '/'
                    file = ''

                data.append(DiscoveredFile(self.name, path, file, filetype, spl[2], spl[1], spl[3]))

        except Exception as ex:
            return False # needs sane exception

        return data

    def fetch_protoindex(self, url, ua):
        # download the file in blocks
        read_block_size = 1024*8

        # set up a stream to the file
        headers={'User-Agent': self.crawl_ua, 'Accept-encoding': 'gzip,deflate'}
        page_indexer = requests.get(url + self._cfg.get('Protoindex', 'file_name'),
            stream=True,
            auth=self.crawl_auth,
            verify=self.crawl_sslverify,
            headers=headers)

        if not page_indexer.status_code == 200:
            return Error('Server \'%s\' returned status code %s' % (self.name, str(page_indexer.status_code)))
        else:
            protoindex_max_size = self._cfg.get('Protoindex', 'file_max_size') * 1048576

            # verify server header content-type
            if page_indexer.headers.get('content-type'):
                content_type = page_indexer.headers.get('content-type')
                if not content_type == 'application/x-gzip':
                    return Error('\'%s\' returned wrong content-type for file \'%s\' (%s).' % (self.name, self._cfg.get('Protoindex', 'file_name'), content_type))

            # check server header content-length to determine how big the file is
            if page_indexer.headers.get('content-length'):
                try:
                    protoindex_size = int(page_indexer.headers['content-length'])

                    if protoindex_size > protoindex_max_size:
                        e = Error('Server \'%s\' indexer exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(protoindex_size)))
                        return e
                except Exception as ex:
                    return Error(str(ex))

            d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file
            protoindex = ''

            while True:
                # read a block
                data = page_indexer.raw.read(read_block_size)

                # terminate if it went over the max file size
                if len(protoindex) > protoindex_max_size:
                    e = Error('Server \'%s\' indexer exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(len(protoindex))))
                    return e

                # break if end of download
                if not data: break

                # decompress and append
                protoindex += d.decompress(data)

            return protoindex

    def verify_protoindex(self, protoindex):
        if not protoindex.startswith('# proto-index v=') or not protoindex.endswith('# end proto-index\n'):
            return Error('Could not verify index for \'%s\'' % self.name)

        return True

    def parse_opendir(self):
        data = []
        dirs = ['']

        def parse(opendir_html, rel=''):
            soup = BeautifulSoup(opendir_html)

            if not 'Index of' in soup.title.text and rel == '':
                return Error('Server \'%s\' doesnt seem to have a valid opendir' % self.name)
            elif not 'Index of' in soup.title.text:
                return
            elif rel == '':
                data.append(DiscoveredFile(self.name, '', '', 'd'))

            for t in soup.findAll('tr'):
                path = None
                modified = None
                size = None
                dir = False

                for td in t.findAll('td'):
                    for img in td.findAll('img'):
                        if 'alt' in img.attrs:
                            if img.attrs['alt'] == '[DIR]':
                                dir = True

                    for a in td.findAll('a'):
                        if not a.text == 'Parent Directory':
                            if 'href' in a.attrs:
                                path = a.attrs['href']
                            break

                    if 'align' in td.attrs:
                        if td.attrs['align'] == 'right' and not 'Parent Directory' in t.text:
                            if not modified:
                                modified = td.text.replace(' ', '')
                            elif not size:
                                size = td.text.replace(' ', '')
                                if size == '-': size = ''

                if path:
                    full = rel+path
                    if '/' in full:
                        spl = full.split('/')
                        relative = '/'.join(spl[:-1])+'/'
                        filename = spl[-1]
                    else:
                        relative = rel
                        filename = path

                    data.append(DiscoveredFile(self.name, relative, filename, 'd' if dir else 'f', size, modified, None))
                    if dir: dirs.append(rel+path)

        while dirs:
            try:
                url = self.crawl_url + dirs[0]
                response = requests.get(url,
                    verify=self.crawl_sslverify,
                    auth=self.crawl_auth,
                    headers={'User-Agent': self.crawl_ua})

                if not response.status_code == 200:
                    raise requests.ConnectionError

                parsed = parse(response.content, dirs[0])

                if isinstance(parsed, Error):
                    return Error

                dirs.pop(0)

            except Exception as ex:
                return Error(str(ex)) # change to something more sane

        return data