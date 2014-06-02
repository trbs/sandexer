from gevent import monkey; monkey.patch_all()
from datetime import datetime
from pymongo import MongoClient
from bin.utils import isInt, Debug

class DiscoveredFile():
    def __init__(self, host_name, path, name, filetype, size=None, modified=None, perm=None):
        self.host_name = host_name
        self.filepath = path
        self.filename = name
        self.filesize = int(size) if isInt(size) else size
        self.filetype = filetype
        self.filemodified = modified
        self.fileperm = int(perm) if isInt(perm) else perm


class MongoDb():
    def __init__(self, cfg):
        self._cfg = cfg
        self._client = MongoClient(self._cfg.get('Database', 'source'))
        self.db = self._client.Sanderex

    def query(self, collection, query):
        return self.db[collection].find(query)

    def try_add_files(self, discovered_files):
        inserts = 0
        start = datetime.now()
        for df in discovered_files:

            # check if it is already in the database
            query = {'filepath': df.filepath,
                     'filetype': df.filetype,
                     'filename': df.filename,
                     'host_name': df.host_name}

            if self.query('files', query).count() != 0:
                continue

            insertdata = {
                'host_name': df.host_name,
                'filetype': df.filetype,
                'filesize': df.filesize,
                'filepath': df.filepath,
                'modified': datetime.now(),
                'filename': df.filename,
                'perm': df.fileperm,
                'filename_clean': '',
                'section': '',
                'imdb': ''
            }

            try:
                self.db.files.insert(insertdata)
                inserts += 1
            except Exception as ex:
                return Debug(str(ex))

        end = datetime.now()

        print 'INSERTS: ' + str((end - start).total_seconds()) + ' seconds'

        return inserts