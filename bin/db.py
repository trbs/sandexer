import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.pool import Pool
from bin.utils import Debug
from datetime import datetime
from bin.psycopg2_pool import PostgresConnectionPool

class Postgres():
    def __init__(self, cfg):
        self._cfg = cfg
        self._pool = None
        self._gevent_poolsize = 10
        self._dsn = 'host=%s port=%s dbname=%s user=%s password=%s' % (
            self._cfg.get('Postgres', 'host'),
            self._cfg.get('Postgres', 'port'),
            self._cfg.get('Postgres', 'db'),
            self._cfg.get('Postgres', 'user'),
            self._cfg.get('Postgres', 'pass'))

        try:
            self._pool = PostgresConnectionPool(self._dsn, maxsize=20)

        except Exception as ex:
            Debug('Could not connect to database: %s' % str(ex))

    def try_add_files(self, discovered_files):
        start = datetime.now()
        inserts = 0
        jobs = []
        job_pool = Pool(self._gevent_poolsize)

        for df in discovered_files:
            sql = 'SELECT is_directory, filepath, filename from ' + '\"files_WipKip\"' + ' WHERE filepath=%s AND filename=%s AND is_directory=%s'
            data = (df.filepath, df.filename, str(df.isdir))

            result = self._pool.fetchone(sql, data)

            if not result:
                # to-do: fix sqli lmao
                sql = 'INSERT INTO ' + '\"files_WipKip\"' + ' (is_directory, filename,filesize, filepath,filemodified, fileperm) VALUES (%s, %s, %s, %s ,%s ,%s)'

                data = (str(df.isdir),
                        df.filename, df.filesize,
                        df.filepath, None,
                        420)

                jobs.append(job_pool.spawn(self._pool.execute, sql, data))

            inserts += 1

        gevent.joinall(jobs)

        end = datetime.now()
        print 'INSERTS: ' + str((end - start).total_seconds()) + ' seconds for %s items' % inserts

        return inserts


#class MongoDb():
#    def __init__(self, cfg):
#        self._cfg = cfg
#        self._client = MongoClient(self._cfg.get('Database', 'source'))
#        self.db = self._client.Sanderex
#
#    def query(self, collection, query):
#        return self.db[collection].find(query)
#
#    def try_add_files(self, discovered_files):
#        inserts = 0
#        start = datetime.now()
#        for df in discovered_files:
#
#            # check if it is already in the database
#            query = {'filepath': df.filepath,
#                     'filetype': df.filetype,
#                     'filename': df.filename,
#                     'host_name': df.host_name}
#
#            if self.query('files', query).count() != 0:
#                continue
#
#            insertdata = {
#                'host_name': df.host_name,
#                'filetype': df.filetype,
#                'filesize': df.filesize,
#                'filepath': df.filepath,
#                'modified': datetime.now(),
#                'filename': df.filename,
#                'perm': df.fileperm,
#                'filename_clean': '',
#                'section': '',
#                'imdb': ''
#            }
#
#            try:
#                self.db.files.insert(insertdata)
#                inserts += 1
#            except Exception as ex:
#                return Debug(str(ex))
#
#        end = datetime.now()
#
#        print 'INSERTS: ' + str((end - start).total_seconds()) + ' seconds'
#
#        return inserts