__author__ = 'dsc'
from bottle import request
from bin.dataobjects import Sources, DataObjectManipulation

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