__author__ = 'dsc'
from bottle import request
import requests
from bin.urlparse import ParseUrl
from bin.protocols import Web
from json import dumps
from bin.orm import Source, SourceFile
from bin.crawler import WebCrawl
from bin.dataobjects import DataObjectManipulation
from bin.utils import Debug

class Api():
    def __init__(self, cfg):
        self._uri = 'post'
        self._cfg = cfg

    def postd(self):
        return request.forms

    def post_get(self, name, default=''):
        return request.POST.get(name, default).strip()

    def handle_post(self, data, db=None, database=None):
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
                            'auth': '',
                            'textcolor': 'red'
                        }
                    })

                auth = ''
                status = []

                if 'www-authenticate' in res.headers:
                    auth = res.headers['www-authenticate']
                    auth = 'DIGEST' if auth.lower().startswith('digest') else 'BASIC'
                    status.append('Requires: %s' % auth)

                if res.status_code == 200 or res.status_code == 401:
                    status.append('Status: OK')

                    return dumps({
                        'detecturl':{
                            'status': ' - '.join(status),
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

        elif data['cmd'][0] == 'get_source_details':
            if not 'source_name' in data:
                return None

            sources = Sources(db, self._cfg)
            sources.get_sources()

            for source in sources.list:
                if source.name == data['source_name'][0]:
                    dom = DataObjectManipulation()
                    source = dom.humanize(source, humansizes=True, humandates=True)
                    source_info = dom.dictionize(source)

                    return {'get_source_details': source_info}

        elif data['cmd'][0] == 'crawlnow' and 'source_name' in data:
            source_name = data['source_name'][0]
            source = db.query(Source).filter_by(name=source_name).first()

            if source:
                webcrawl = WebCrawl(
                    name=source_name,
                    cfg=self._cfg,

                    url = source.crawl_url,
                    ua = source.crawl_useragent,
                    auth_type=source.crawl_authtype,
                    auth_username=source.crawl_username,
                    auth_password=source.crawl_password,
                    crawl_wait=source.crawl_wait,
                    ssl_verify=source.crawl_verifyssl
                )
                res = webcrawl.http()
                if isinstance(res, Debug):
                    return Debug

                database.bulk_add(db, res, source_name)

            return dumps({'crawlnow': {
                'status': 'busy'
            }})
            pass

        return None