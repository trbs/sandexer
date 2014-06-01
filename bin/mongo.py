from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient

class MongoDb():
    def __init__(self):
        self._client = MongoClient()
