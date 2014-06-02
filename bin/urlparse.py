# dsc@code.own3d.be | 2-6-2014

import cgi,urllib2

class ParseUrl():
    def __init__(self, uri):
        self.scheme = ''
        self.fulluri = self.get_fulluri(uri)
        self.base = self.get_base(self.fulluri)
        self.domain = self.get_domain(self.base)
        self.path = self.get_path(self.fulluri)
        self.reluri = self.get_reluri(self.fulluri)

        if len(self.base.split('.')) == 2 and not self.fulluri.startswith('ftp://'):
            self.base = 'www.' + self.base
            self.fulluri = '%swww.%s' % (self.scheme, self.fulluri[len(self.scheme):])

        self.unquoted_uri = self.unquote_uri()

    def get_reluri(self, uri):
        uri = self.strip_scheme(uri)
        if uri.endswith('/'):
            uri = uri[:-1]

        if not '/' in uri:
            return self.scheme + uri + '/'
        if '/' in uri and not uri.endswith('/'):
            spl = uri.split('/')
            for a in ['.html', 'htm', '.php', '.aspx', '.asp']:
                if a in spl[len(spl)-1]:
                    return self.scheme + '/'.join(spl[:-1]) + '/'  # fml
            return self.scheme + '/'.join(spl) + '/'
        return '?!'

    def get_fulluri(self, uri):
        if uri.endswith('/'):
            uri = uri[:-1]

        for s in ['http://', 'https://', 'ftp://']:
            if uri.startswith(s):
                self.scheme = s
                return uri

        self.scheme = 'http://'
        return 'http://%s' % uri

    def get_base(self, uri):
        uri = self.strip_scheme(uri)
        return uri[:uri.find('/')] if '/' in uri else uri

    def get_domain(self, uri):
        spl = uri.split('.')
        if len(spl) == 4:
            for s in spl:
                try:
                    int(s)
                    return uri
                except:
                    break
        return '.'.join(spl[-2:]) if len(spl) > 1 else uri

    def get_path(self, uri):
        uri = self.strip_scheme(uri)
        return uri[uri.find('/'):] if '/' in uri else None

    def strip_scheme(self, uri):
        if uri.startswith('http://'):
            return uri[7:]
        elif uri.startswith('https://'):
            return uri[8:]
        elif uri.startswith('ftp://'):
            return uri[6:]
        else:
            return uri

    def unquote_uri(self):
        return cgi.escape(urllib2.unquote(self.fulluri))