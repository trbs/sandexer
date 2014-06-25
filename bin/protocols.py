from bin.dataobjects import Debug
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import requests


class Web():
    def __init__(self, cfg):
        self._cfg = cfg
        self.ua = cfg.get('Crawler', 'default_ua')

    def request(self, url, request_method, crawl_auth=None, crawl_auth_type=None, crawl_ua='', verifyssl=False, headers=None, stream=False, redirects=True):
        if not crawl_ua:
            crawl_ua = self.ua

        try:
            response = request_method(
                url,
                stream=stream,
                auth=crawl_auth,
                allow_redirects=redirects,
                verify=verifyssl,
                headers=headers if headers else {'User-Agent': crawl_ua},
                timeout=self._cfg.get('Crawler', 'timeout'))

            if response.status_code == 200 or response.status_code == 301:
                return response

            elif response.status_code == 401:
                if 'www-authenticate' in response.headers:
                    auth = response.headers['www-authenticate'].lower()

                    if auth.startswith('basic'):
                        if not crawl_auth:
                            return Debug('url: \'%s\' - Requires BASIC authentication. None provided.' % url)

                        elif crawl_auth_type is HTTPDigestAuth:
                            return Debug('url: \'%s\' - BASIC authentication required (tried DIGEST).' % url)

                    elif auth.startswith('digest'):
                        if not crawl_auth:
                            return Debug('url: \'%s\' - Requires DIGEST authentication. None provided.' % url)
                        elif crawl_auth_type is HTTPBasicAuth:
                            return Debug('url: \'%s\' - DIGEST authentication required (tried BASIC).' % url)

                return Debug('url: \'%s\' - Invalid authentication.' % url)
            else:
                return Debug('url: \'%s\' - Invalid status code \'%s\'' % (url, str(response.status_code)))

        except requests.exceptions.Timeout:
            return Debug('url: \'%s\' - Timeout error.' % url)
        except requests.ConnectionError:
            return Debug('url: \'%s\' - Connection error. Is the server up?' % url)
        except Exception as ex:
            return Debug('url: \'%s\' - Undefined error: %s' % (url, str(ex)))