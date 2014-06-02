'''
Crawwwwwlinnn in myyyyy skinnnnnnnn
'''
from gevent import monkey; monkey.patch_all()
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
import ftplib
from datetime import datetime
from bs4 import BeautifulSoup
import zlib
from mongo import DiscoveredFile
from bin.utils import isInt
from bin.utils import Debug

#to-do:
# support HTTP/SMB/FTP/AFP
# 0. dont care about sharetraps (301's and such)
# 1. 00INDEX.xz - https://docs.python.org/dev/library/lzma.html
# 2. 00INDEX.gz - (done)
# 3. 00SHARE
# 4. opendir

class FtpCrawl():
    def __init__(self, cfg, db, name, url, auth_username=None, auth_password=None):
        self._cfg = cfg
        self._db = db
        self.name = name
        self.crawl_url = url
        self.auth_username = auth_username if auth_username else 'anonymous'
        self.auth_password = auth_password if auth_password else 'anonymous'

    def ftp(self):
        ftp = ftplib.FTP(self.crawl_url)
        ftp.login(self.auth_username, self.auth_password)

        files = []

        try:
            files = ftp.nlst()
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":
                print "No files in this directory"
            else:
                raise

        for f in files:
            print f

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
        response_head = self.request(
            url=self.crawl_url.reluri,
            request_method=requests.head)

        if isinstance(response_head, Debug):
            # Website not found
            return response_head
        else:
            discovered_files = None

            # try fetching protoindexer
            protoindexer = self.fetch_protoindex(self.crawl_url.reluri)

            if isinstance(protoindexer, Debug):
                pass
            else:
                verify = self.verify_protoindex(protoindexer)

                # if the indexer verification fails it'll fall back to opendir crawling
                if not isinstance(verify, Debug):
                    discovered_files = self.parse_protoindex(protoindexer)

            if not discovered_files:
                # go for opendir
                discovered_files = self.walk_opendir()

            if isinstance(discovered_files, Debug):
                # if that also fails, quit trying
                return discovered_files

            if len(discovered_files) == 0:
                return 0
            else:
                return self._db.try_add_files(discovered_files)

    def parse_protoindex(self, protoindex):
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
            return Debug(str(ex))

        return data

    def fetch_protoindex(self, url):
        try:
            # download the file in blocks
            read_block_size = 1024*8

            # set up a stream to the file
            response_indexer = self.request(
                url=url + self._cfg.get('Protoindex', 'file_name'),
                request_method=requests.get,
                headers={'User-Agent': self.crawl_ua,
                         'Accept-encoding': 'gzip,deflate'},
                stream=True)

            if isinstance(response_indexer, Debug):
                return response_indexer

            protoindex_max_size = self._cfg.get('Protoindex', 'file_max_size') * 1048576

            # verify server header content-type
            if response_indexer.headers.get('content-type'):
                content_type = response_indexer.headers.get('content-type')

                if not content_type == 'application/x-gzip':
                    return Debug('Source \'%s\' - Invalid content-type for file \'%s\' (%s).' % (self.name, self._cfg.get('Protoindex', 'file_name'), content_type))

            # check server header content-length to determine how big the file is
            if response_indexer.headers.get('content-length'):
                protoindex_size = int(response_indexer.headers['content-length'])

                if protoindex_size > protoindex_max_size:
                    return Debug('Source \'%s\' - Indexer exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(protoindex_size)))

            d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file
            protoindex = ''

            while True:
                # read a block
                data = response_indexer.raw.read(read_block_size)

                # terminate if it went over the max file size
                if len(protoindex) > protoindex_max_size:
                    return Debug('Source \'%s\' - Indexer exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(len(protoindex))))

                # break if end of download
                if not data: break

                # decompress and append
                protoindex += d.decompress(data)

            return protoindex

        except Exception as ex: # gotta catch 'm all
            return Debug(str(ex))

    def verify_protoindex(self, protoindex):
        if not protoindex.startswith('# proto-index v=') or not protoindex.endswith('# end proto-index\n'):
            return Debug('Source \'%s\' - Could not verify index' % self.name)

        return True

    def walk_opendir(self):
        import time
        time.sleep(float(0.5))
        discovered_files = []
        dirs = ['']

        while dirs:
            try:
                response = self.request(
                    url=self.crawl_url.reluri + dirs[0],
                    request_method=requests.get,
                    redirects=False
                )

                if isinstance(response, Debug):
                    dirs.pop(0)
                    continue

                parsed = self.parse_opendir(response, discovered_files, dirs, dirs[0])

                if isinstance(parsed, Debug):
                    # do not store invalid opendirs
#                    for i in range(0, len(discovered_files)):
#                        if discovered_files[i].filename == dirs[0]:
#                            discovered_files.pop(i)
#                            break

                    dirs.pop(0)
                    continue

                discovered_files = parsed[0]
                dirs = parsed[1]

                dirs.pop(0)

            except Exception as ex:
                return Debug(str(ex))

        e = 'e'
        print len(discovered_files)
        import sys
        sys.exit()
        #return discovered_files

    def parse_opendir(self, response, discovered_files, dirs, rel=''):
        # i do not expect you to understand the following code

        opendir_html = response.content
        soup = BeautifulSoup(opendir_html)

        if not soup.title.text.startswith('Index of') and not soup.title.text.startswith(self.crawl_url.base + ':/'):
            return Debug('Source \'%s\' - Invalid opendir (\'%s\')' % (self.name, response.url))

        if not '<h1>Index of' in response.content:
            return Debug('Source \'%s\' - Invalid opendir (\'%s\')' % (self.name, response.url))

        if rel == '':
            discovered_files.append(DiscoveredFile(self.name, '', '', 'd'))

        for t in soup.findAll('a'):
            if 'href' in t.attrs:
                if not '?C=' in t.attrs['href'] and not 'parent directory' in t.text.lower():
                    filename = t.attrs['href']
                    isdir = True if filename.endswith('/') else False
                    modified = None
                    size = None

                    a = t.parent
                    b = t.parent.text
                    c = b[:b.find('\n')].split(' ')

                    if a.text.endswith('</li>'):
                        pass
                    elif len(c) > 1:
                        a = t.parent.text
                        a = a[:a.find('\n')]
                        spl = [z for z in a.split(' ') if z]
                    else:
                        a = a.parent.text[len(filename):]
                        spl = [filename] + [z for z in a.split(' ') if z]

                    if spl[0] == filename and len(spl) > 1:
                        modified = '%s %s' % (spl[1], spl[2])
                        size = None if spl[3] == '-' else spl[3].replace(' ', '')

                    discovered_files.append(DiscoveredFile(self.name, rel, filename, 'd' if isdir else 'f', size, modified, None))
                    if isdir: dirs.append(rel+filename)

        return [discovered_files, dirs]

    def request(self, url, request_method, headers=None, stream=False, redirects=True):
        try:
            response = request_method(
                url,
                stream=stream,
                auth=self.crawl_auth,
                allow_redirects=redirects,
                verify=self.crawl_sslverify,
                headers=headers if headers else {'User-Agent': self.crawl_ua},
                timeout=self._cfg.get('Crawler', 'timeout'))

            if response.status_code == 200 or response.status_code == 301:
                return response

            elif response.status_code == 401:
                if 'www-authenticate' in response.headers:
                    auth = response.headers['www-authenticate'].lower()

                    if auth.startswith('basic'):
                        if not self.crawl_auth:
                            return Debug('Source \'%s\' - Requires BASIC authentication. None provided.' % self.name)

                        elif self.crawl_auth_type is HTTPDigestAuth:
                            return Debug('Source \'%s\' - BASIC authentication required for accessing \'%s\'. (tried DIGEST).' % (self.name, url))

                    elif auth.startswith('digest'):
                        if not self.crawl_auth:
                            return Debug('Source \'%s\' - Requires DIGEST authentication. None provided.' % self.name)
                        elif self.crawl_auth_type is HTTPBasicAuth:
                            return Debug('Source \'%s\' - DIGEST authentication required for accessing \'%s\'. (tried BASIC).' % (self.name, url))

                return Debug('Source \'%s\' - Invalid authentication for \'%s\'.' % (self.name, url))
            else:
                return Debug('Source \'%s\' - Invalid status code \'%s\'. (%s)' % (self.name, str(response.status_code), url))

        except requests.exceptions.Timeout:
            return Debug('Source \'%s\' - Timeout error while fetching \'%s\'.' % (self.name, url))
        except requests.ConnectionError:
            return Debug('Source \'%s\' - Connection error while fetching \'%s\'. Is the server up?' % (self.name, url))
        except Exception as ex:
            return Debug('Source \'%s\' - Undefined error while fetching \'%s\'.' % (self.name, url))