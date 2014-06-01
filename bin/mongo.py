from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient

class MongoDb():
    def __init__(self, cfg):
        self._cfg = cfg
        self._client = MongoClient(self._cfg.get('Database', 'source'))
        self.db = self._client.Sanderex

    def query(self, collection, query):
        return self.db[collection].find(query)