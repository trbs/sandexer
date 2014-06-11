import gevent
import gevent.monkey
gevent.monkey.patch_all()
import os
from gevent.pool import Pool
from bin.utils import Debug, generate_string
from datetime import datetime
from bin.psycopg2_pool import PostgresConnectionPool, ProgrammingError
import random

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

    def init_db(self):
        sql = 'SELECT count(*) from sources'
        try:
            return self._pool.execute(sql)
        except ProgrammingError:
            return self._pool.execute('''
                CREATE TABLE sources
                (
                  name text NOT NULL,
                  added timestamp without time zone NOT NULL,
                  crawl_protocol text NOT NULL,
                  crawl_username text,
                  crawl_password text,
                  crawl_authtype text,
                  crawl_url text,
                  crawl_interval bigint,
                  crawl_useragent text NOT NULL,
                  crawl_verifyssl boolean NOT NULL DEFAULT false,
                  crawl_lastcrawl timestamp without time zone,
                  bandwidth text,
                  color integer,
                  filetypes integer[] NOT NULL -- 0: Random files...
                )
                WITH (
                  OIDS=FALSE
                );
                ALTER TABLE sources
                  OWNER TO sanderex;
                COMMENT ON COLUMN sources.filetypes IS '
                0: Random files
                1: Documents
                2: Movies
                3: Music
                4: Pictures';
            ''')

    def add_source(self, source_name, options):
        sql = 'SELECT name FROM sources WHERE name=\'%s\'' % source_name

        result = self._execute(sql)

        if not result == 0:
            return Debug('Source \'%s\' already exists' % source_name)

        sql = 'SELECT count(*) FROM \"files_%s\";' % source_name
        result = self._execute(sql)

        if not isinstance(result, Debug):
            self._execute('DROP TABLE \"files_%s\";' % source_name)

        sql = '''
            CREATE TABLE "files_%s"
            (
              is_directory boolean NOT NULL,
              filename name,
              filesize bigint,
              filepath text,
              filemodified timestamp without time zone,
              fileperm integer,
              id serial NOT NULL,
              fileadded timestamp without time zone NOT NULL,
              CONSTRAINT por PRIMARY KEY (id )
            )
            WITH (
              OIDS=FALSE
            );
            ALTER TABLE "files_WipKip"
              OWNER TO sanderex;
        ''' % source_name

        result = self._execute(sql)

        if isinstance(result, Debug):
            return result

        # set up options here

        return True



    def add_files(self, discovered_files, source_name):
        # to-do:
        # 1. watch out for sqli trough table_name

        start = datetime.now()

        sql = 'DELETE FROM \"files_%s\";' % source_name
        self._execute(sql)

        temp = '%s/tmp/%s' % (self._cfg.app_root, generate_string(random.randrange(5,12)) + '.crawl')
        f = open(temp, 'w')

        inserts = 0
        for df in discovered_files:
            isdir = str(df.isdir).lower()[:1]
            line = '%s|%s|%s|%s|%s|%s|%s|%s\n' % (isdir, df.filename, df.filesize, df.filepath, df.filemodified, df.fileperm, inserts+1, df.fileadded)
            f.write(line)
            inserts += 1

        f.close()

        # to-do
        # 1. https://pythonhosted.org/psycopg2/cursor.html#cursor.copy_expert
        #    should work without having to use postgres superuser privs
        sql = 'COPY \"files_%s\" FROM \'%s\' DELIMITER \'|\' NULL \'None\';' % (source_name, temp)
        self._execute(sql)

        os.remove(temp)
        end = datetime.now()
        Debug('Source %s - %s seconds for %s item INSERTS' % (source_name, str((end - start).total_seconds()),inserts))

    def _execute(self, sql):
        try:
            return self._pool.execute(sql)
        except Exception as ex:
            return Debug('Could not execute SQL command: %s\n--\n%s--' % (sql ,str(ex)), warning=True)

#    def try_add_files(self, discovered_files):
#        start = datetime.now()
#        inserts = 0
#        jobs = []
#        job_pool = Pool(self._gevent_poolsize)
#
#        for df in discovered_files:
#            sql = 'SELECT is_directory, filepath, filename from ' + '\"files_WipKip\"' + ' WHERE filepath=%s AND filename=%s AND is_directory=%s'
#            data = (df.filepath, df.filename, str(df.isdir))
#
#            result = self._pool.fetchone(sql, data)
#
#            if not result:
#                # to-do: fix sqli lmao
#                sql = 'INSERT INTO ' + '\"files_WipKip\"' + ' (is_directory, filename,filesize, filepath,filemodified, fileperm) VALUES (%s, %s, %s, %s ,%s ,%s)'
#
#                data = (str(df.isdir),
#                        df.filename, df.filesize,
#                        df.filepath, None,
#                        420)
#
#                jobs.append(job_pool.spawn(self._pool.execute, sql, data))
#
#            inserts += 1
#
#        gevent.joinall(jobs)
#
#        end = datetime.now()
#        print 'INSERTS: ' + str((end - start).total_seconds()) + ' seconds for %s items' % inserts
#
#        return inserts