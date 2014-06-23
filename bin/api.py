__author__ = 'dsc'
from bottle import request
import requests
from bin.urlparse import ParseUrl
from bin.protocols import Web
from json import dumps
from bin.dataobjects import Sources, DataObjectManipulation
from bin.utils import Debug

class Api():
    def __init__(self, db, cfg):
        self._uri = 'post'
        self._db = db
        self._cfg = cfg

    def postd(self):
        return request.forms

    def post_get(self, name, default=''):
        return request.POST.get(name, default).strip()

    def handle_post(self, data):
        if not 'cmd' in data:
            return None

        data = data.dict

        if data['cmd'][0] == 'detecturl' and 'url' in data:
            url = data['url'][0]

            if url.startswith('http') or url.startswith('https') or url.startswith('HTTP') or url.startswith('HTTPS'):

                try:
                    url = ParseUrl(url)
                except:
                    return dumps({'detecturl': 'Could not parse location.'})
                try:
                    res = requests.head(url=url.reluri,verify=False, allow_redirects=False, headers={'User-Agent': self._cfg.get('Crawler', 'default_ua')})
                except:
                    return dumps({
                        'detecturl':{
                            'status': 'Status: Error',
                            'auth': None,
                            'textcolor': 'red'
                        }
                    })

                auth = None
                status = []

                if 'www-authenticate' in res.headers:
                    auth = res.headers['www-authenticate']
                    auth = 'DIGEST' if auth.lower().startswith('digest') else 'BASIC'
                    status.append('Requires: %s' % auth)

                if res.status_code == 200 or res.status_code == 401:
                    status.append('Status: OK')

                    return dumps({
                        'detecturl':{
                            'status': '<br>'.join(status),
                            'auth': auth,
                            'textcolor': 'green'
                        }
                    })
                elif res.status_code == 301:
                    return dumps({
                        'detecturl':{
                            'status': 'Status: HTTP redirect encountered (301)',
                            'auth': auth,
                            'textcolor': 'red'
                        }
                    })

        if data['cmd'][0] == 'get_source_details':
            if not 'source_name' in data:
                return None

            sources = Sources(self._db, self._cfg)
            sources.get_sources()

            for source in sources.list:
                if source.name == data['source_name'][0]:
                    dom = DataObjectManipulation()
                    source = dom.humanize(source, humansizes=True, humandates=True)
                    source_info = dom.dictionize(source)

                    return {'get_source_details': source_info}

        return None