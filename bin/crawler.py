'''
Crawwwwwlinnn in myyyyy skinnnnnnnn
'''
from gevent import monkey; monkey.patch_all()
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests
import ftplib
import dateutil.parser
from bin.files import Fileformats
from bytes2human import human2bytes
from random import randrange
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
import zlib
from bin.urlparse import ParseUrl
from bin.orm import SourceFile
from bin.utils import isInt
from bin.protocols import Web
from bin.dataobjects import Debug

#to-do:
# support SMB/FTP/AFP
# 1. 00INDEX.xz - https://docs.python.org/dev/library/lzma.html
# 2. 00SHARE

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
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self._cfg = kwargs['cfg']
        self._web = Web(cfg=self._cfg)

        self.crawl_url = kwargs['url'] if 'url' in kwargs else None
        self.crawl_ua = kwargs['ua'] if 'ua' in kwargs else self._cfg.get('Crawler', 'default_ua')
        self.crawl_sslverify = kwargs['ssl_verify'] if 'ssl_verify' in kwargs else self._cfg.get('Crawler', 'verify_ssl')

        if 'auth_type' in kwargs:
            if kwargs['auth_type'] == 'HTTP_BASIC':
                self.crawl_auth_type = HTTPBasicAuth
            elif kwargs['auth_type'] == 'HTTP_DIGEST':
                self.crawl_auth_type = HTTPDigestAuth
            else:
                self.crawl_auth_type = None
        else:
            self.crawl_auth_type = None

        if 'auth_username' in kwargs and 'auth_password' in kwargs:
            username = kwargs['auth_username']
            password = kwargs['auth_password']
            if username and password:
                self.crawl_auth = self.crawl_auth_type(kwargs['auth_username'], kwargs['auth_password'])
            else:
                self.crawl_auth = None
        else:
            self.crawl_auth = None

        self.crawl_wait = kwargs['crawl_wait'] if 'crawl_wait' in kwargs else 0

    def http(self):
        if not isinstance(self.crawl_url, ParseUrl):
            self.crawl_url = ParseUrl(self.crawl_url)

        response_head = self._web.request(
            url=self.crawl_url.reluri,
            request_method=requests.head,
            crawl_auth = self.crawl_auth,
            crawl_auth_type= self.crawl_auth_type,
            crawl_ua = self.crawl_ua,
            verifyssl=self.crawl_sslverify
        )

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


            return discovered_files

    def parse_protoindex(self, protoindex):
        pi = protoindex.split('\n')
        discovered_files = []
        ff = Fileformats(self._cfg)

        try:
            for line in pi[1:-2]:
                if not line.startswith("f") and not line.startswith("d"):
                    continue

                spl = line.split(' ')
                spl[4] = ' '.join(spl[4:])
                spl = spl[:5]

                isdir = True if line.startswith('d') else False
                filepath = '/'
                fileformat = 0
                ext = None
                fileperm = int(spl[3])
                filesize = int(spl[2])

                #if not isdir:
                file_spl = spl[4].split('/')
                filename = file_spl[-1]
                filepath = '/' + '/'.join(file_spl[:-1])
                if not filepath.endswith('/'): filepath += '/'

                if not isdir and '.' in filename:
                    ext = filename.split('.')[-1].lower()
                    fileformat = ff.get_fileformat(ext)

                try:
                    modified = datetime.fromtimestamp(float(spl[1]))
                except:
                    modified = None

                discovered_files.append(DiscoveredFile(self.name, filepath, filename, isdir, filesize, modified, fileperm, fileformat, ext))

        except Exception as ex:
            return Debug(str(ex))

        return discovered_files

    def fetch_protoindex(self, url):
        try:
            # download the file in blocks
            read_block_size = 1024*8

            # set up a stream to the file
            response_indexer = self._web.request(
                url=url + self._cfg.get('Protoindex', 'file_name'),
                request_method=requests.get,
                headers={'User-Agent': self.crawl_ua, 'Accept-encoding': 'gzip,deflate'},
                stream=True,
                crawl_auth=self.crawl_auth,
                crawl_auth_type=self.crawl_auth_type,
                verifyssl=self.crawl_sslverify,
                redirects=False
            )

            if isinstance(response_indexer, Debug):
                return response_indexer

            protoindex_max_size = self._cfg.get('Protoindex', 'file_max_size') * 1048576

            # verify server header content-type
            if response_indexer.headers.get('content-type'):
                content_type = response_indexer.headers.get('content-type')

#                if not content_type == 'application/x-gzip':
#                    return Debug('Source \'%s\' - Invalid content-type for file \'%s\' (%s).' % (self.name, self._cfg.get('Protoindex', 'file_name'), content_type))

            # check server header content-length to determine how big the file is
            if response_indexer.headers.get('content-length'):
                protoindex_size = int(response_indexer.headers['content-length'])

                if protoindex_size > protoindex_max_size:
                    return Debug('Source \'%s\' - Indexer exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(protoindex_size)))

            protoindex = ''
            bytes_fetched = 0
            d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file

            while True:
                # read a block
                data = response_indexer.raw.read(read_block_size)
                bytes_fetched += read_block_size

                # terminate if it went over the max file size
                if bytes_fetched > protoindex_max_size:
                    return Debug('Source \'%s\' - Indexer exceeded max file size \'%s\' (%s). Falling back to parsing webdav.' % (self.name, str(protoindex_max_size), str(len(protoindex))))

                # break if end of download
                if not data: break

                # decompress and append
                protoindex += d.decompress(data)

            return protoindex

        except Exception as ex: # gotta catch 'm all
            return Debug(str(ex))

    def verify_protoindex(self, protoindex):
        # Only 1.0.0 is supported at this time
        if not protoindex.startswith('# proto-index v=1.0.0') or not protoindex.endswith('# end proto-index\n'):
            return Debug('Source \'%s\' - Could not verify index' % self.name)

        return True

    def walk_opendir(self):
        discovered_files = []
        dirs = ['']

        while dirs:
            if self.crawl_wait:
                # cut the source some slack
                #sleep(float(self.crawl_wait))
                pass

            # ignore certain directories
            if dirs[0] == 'CCC/pub/':
                dirs.pop(0)
                continue

            # dont go backwards
            if '..' in dirs[0]:
                dirs.pop(0)
                continue

            # detect a loop
            if dirs[0] and isinstance(Discovery().detect_loop(self.name, dirs[0]), Debug):
                d = Discovery()
                discovered_files = d.fix_looped_discoveries(discovered_files, dirs[0])

                dirs.pop(0)
                continue
            try:
                if self.crawl_url.reluri.endswith('/') and dirs[0].startswith('/'):
                    self.crawl_url.reluri = self.crawl_url.reluri[:-1]

                # fetch opendir
                response = self._web.request(
                    url=self.crawl_url.reluri + dirs[0],
                    request_method=requests.get,
                    redirects=False,
                    crawl_auth=self.crawl_auth,
                    crawl_auth_type=self.crawl_auth_type,
                    crawl_ua=self.crawl_ua
                )

                if isinstance(response, Debug):
                    if dirs[0] == '':
                        return response
                    dirs.pop(0)
                    continue

                # try reading it
                parsed = self.parse_opendir(response, discovered_files, dirs, dirs[0])

                if isinstance(parsed, Debug):
                    if dirs[0] == '':
                        return Debug('Source \'%s\' - No opendir at (\'%s\')' % (self.name, self.crawl_url.reluri + dirs[0]))
                    dirs.pop(0)
                    continue

                # yay
                discovered_files = parsed[0]
                dirs = parsed[1]

                dirs.pop(0)

            except Exception as ex:
                return Debug(str(ex))

        print 'Discovered: ' + str(len(discovered_files))
        return discovered_files

    def verify_opendir(self, soup, response):
        if soup.title:
            if soup.title.text.startswith('Index of') or \
               soup.title.text.startswith(self.crawl_url.base + ':/'):
                if '<h1>Index of' in response.content:
                    return True

        return Debug('Source \'%s\' - Invalid opendir (\'%s\')' % (self.name, response.url))

    def parse_opendir(self, response, discovered_files, dirs, rel=''):
        opendir_html = response.content
        # if the opendir contains a lot of files, divide the html in chunks so beautifulsoup parses faster
        # unncesary for fast machines but optimization is always nice
        page_size = len(opendir_html)
        chunks = []
        chunk_size = 15000 # in characters

        if page_size > chunk_size:
            head = opendir_html[:chunk_size]
            soup = BeautifulSoup(head)
            verify = self.verify_opendir(soup, response)

            if isinstance(verify, Debug):
                return verify

            spl = []
            spl_tag = ''
            if '<img' in opendir_html:
                spl = opendir_html.split('<img')
                spl_tag = '<img'
            elif '<a' in opendir_html:
                spl = opendir_html.split('<a')
                spl_tag = '<a'
            else:
                return [discovered_files, dirs]

            avg = len(spl[randrange(1,len(spl))]) + 15
            chunk_div = chunk_size / avg

            chunks = [spl_tag.join(spl[x:x + chunk_div]) for x in xrange(0, len(spl), chunk_div)]
        else:
            soup = BeautifulSoup(opendir_html)
            verify = self.verify_opendir(soup, response)

            if isinstance(verify, Debug):
                return verify

            chunks = [opendir_html]

        for chunk in chunks:
            soup = BeautifulSoup(chunk)
            ff = Fileformats(self._cfg)

            # do not try to understand the following
            # to-do:
            # 1. needs more exception handling

            for t in soup.findAll('a', href=True):
                filename = t.attrs['href']

                if '?C=' in filename or 'parent directory' in t.text.lower():
                    continue

                if filename.startswith('./'):
                    filename = filename[2:]

                isdir = True if filename.endswith('/') else False
                modified = None
                size = None
                ext = None
                fileformat = 0

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
                    if spl[3] == '-':
                        size = None
                    else:
                        size = spl[3].replace(' ', '')
                        try:
                            size = human2bytes(size)
                        except:
                            size = None

                try:
                    modified = dateutil.parser.parse(modified)
                except:
                    modified = None

                rel = '/' if not rel else rel
                if not rel.startswith('/'): rel = '/' + rel

                if not isdir and '.' in filename:
                    ext = filename.split('.')[-1].lower()
                    fileformat = ff.get_fileformat(ext)

                if isdir:
                    if filename.endswith('/'):
                        dirs.append(rel+filename)
                        filename = filename[:-1]
                    else:
                        dirs.append(rel+filename)

                discovered_files.append(DiscoveredFile(self.name, '/' if not rel else rel, filename, isdir, size, modified, None, fileformat=fileformat, fileext=ext))

        return [discovered_files, dirs]

class DiscoveredFile():
    def __init__(self, source_name, path, name, isdir, size=None, modified=None, perm=None, fileformat=None, fileext=None, fileadded=None):
            self.source_name = source_name
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

class Discovery():
    def __init__(self):
        self._max_loops = 3

    def detect_loop(self, source_name, path):
        spl = path.split('/')[:-1][::-1]

        if len(spl) > self._max_loops - 1 and \
           spl[0] == spl[1] and \
           spl[0] == spl[2]:
                return Debug('Source \'%s\' - Possible loop found (\'%s\'). Cleaning up previously indexed files from in the loop...' % (source_name, path))

        return False

    def fix_looped_discoveries(self, discovered_files, path):
        spl = path.split('/')[:-1][::-1]
        not_further = '/'.join(spl[self._max_loops - 1:][::-1]) + '/'

        new = []
        for z in discovered_files:
            if not z.filepath.startswith(not_further):
                new.append(z)
            elif not z.isdir:
                if z.filepath == not_further:
                    new.append(z)
                elif not not_further.endswith(z.filepath.split('/')[-2] + '/'):
                    new.append(z)
            else:
                if not z.filepath > not_further and not not_further.endswith(z.filename):
                    new.append(z)

        return new
