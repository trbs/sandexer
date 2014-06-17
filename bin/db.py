import gevent
import gevent.monkey
gevent.monkey.patch_all()
from gevent.pool import Pool
from bin.utils import Debug, generate_string
from datetime import datetime
from bin.dataobjects import DiscoveredFile, DataObjectManipulation
from bin.psycopg2_pool import PostgresConnectionPool, ProgrammingError
import random, os, urllib

# to-do:
# clean this up a bit

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

        result = self._pool.execute(sql)

        if isinstance(result, Debug):
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
                  crawl_useragent text,
                  crawl_verifyssl boolean NOT NULL DEFAULT false,
                  crawl_lastcrawl timestamp without time zone,
                  bandwidth text,
                  color integer,
                  filetypes integer[] NOT NULL, -- 0: Random files...
                  sources_id serial NOT NULL,
                  description text,
                  total_size bigint,
                  total_files bigint,
                  thumbnail_url text,
                  country text,
                  filedistribution_files integer,
                  filedistribution_documents integer,
                  filedistribution_movies integer,
                  filedistribution_music integer,
                  filedistribution_pictures integer,
                  tags text[],
                  html_header text,
                )
                WITH (
                  OIDS=FALSE
                );
                ALTER TABLE sources
                  OWNER TO %s;
                COMMENT ON COLUMN sources.filetypes IS '
                0: Random files
                1: Documents
                2: Movies
                3: Music
                4: Pictures';
            ''' % self._cfg.get('Postgres', 'db'))

    def fetch_sources(self):
        select_sql = 'SELECT * from sources'
        column_sql = 'select column_name from information_schema.columns where table_name=\'sources\';'

        select_results = []
        column_results = []

        try:
            select_results = self._pool.fetchall(select_sql)
        except:
            return Debug('Could not fetch table sources')

        try:
            column_results = [''.join(z) for z in self._pool.fetchall(column_sql)]
        except:
            return Debug('Could not fetch table names')

        return {'columns': column_results[::-1],
                'results': select_results}

    def add_source(self, source_name, opts):
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
              filename text,
              filesize bigint,
              filepath text,
              filemodified timestamp without time zone,
              fileperm integer,
              id serial primary key,
              fileadded timestamp without time zone NOT NULL,
              fileext text,
              fileformat integer,
              download_count integer
            )
            WITH (
              OIDS=FALSE
            );
            ALTER TABLE "files_%s"
              OWNER TO %s;
        ''' % (source_name, source_name, self._cfg.get('Postgres', 'db'))

        result = self._execute(sql)

        if isinstance(result, Debug):
            return result

        # set up options here

        return True

    def add_files(self, discovered_files, source_name):
        # All of the sql queries should be save from SQL injection IF the source name is alphanummeric!
        start = datetime.now()

        sql = 'DELETE FROM \"files_%s\";' % source_name
        self._execute(sql)

        temp = '/tmp/%s.crawl' % generate_string(random.randrange(5,12))
        f = open(temp, 'w')

        inserts = 0
        total_size = 0
        total_files = 0
        filedistribution = [0, 0, 0, 0, 0]

        for df in discovered_files:
            isdir = str(df.isdir).upper()

            df.filename = urllib.quote_plus(df.filename) if df.filename else None
            df.filepath = urllib.quote_plus(df.filepath) if df.filepath else None

            line = '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (isdir, df.filename, df.filesize, df.filepath, df.filemodified, df.fileperm, inserts+1, start, df.fileext, df.fileformat, None)
            f.write(line)

            inserts += 1
            if df.filesize:
                total_size += df.filesize if df.filesize != 4096 else 0

            if not df.isdir and '.' in df.filename:
                filedistribution[df.fileformat] += 1
                total_files += 1

        f.close()

        # to-do
        # 1. https://pythonhosted.org/psycopg2/cursor.html#cursor.copy_expert
        #    should work without having to use postgres superuser privs
        sql = 'COPY \"files_%s\" FROM \'%s\' DELIMITER \'|\' NULL \'None\';' % (source_name, temp)
        self._execute(sql)

        os.remove(temp)
        end = datetime.now()
        Debug('Source %s - %s seconds for %s item INSERTS' % (source_name, str((end - start).total_seconds()),inserts), info=True)

        # Update the total size of the indexed Source
        sql = 'UPDATE sources SET total_size=%s where name=\'%s\';' % (total_size, source_name)
        self._execute(sql)

        # Update the total amount of files of the indexed source
        sql = 'UPDATE sources SET total_files=%s where name=\'%s\';' % (total_files, source_name)
        self._execute(sql)

        # Update the distribution of files
        sql = '''
                UPDATE sources SET (
                    filedistribution_files,
                    filedistribution_documents,
                    filedistribution_movies,
                    filedistribution_music,
                    filedistribution_pictures) =
                (%s, %s, %s, %s, %s) where name=\'%s\';
                ''' % (filedistribution[0],
                       filedistribution[1],
                       filedistribution[2],
                       filedistribution[3],
                       filedistribution[4],
                       source_name)

        self._execute(sql)

        # Update the last crawled time
        # Should be save from sqli as long as source_name is alphanummeric
        sql = 'UPDATE sources SET crawl_lastcrawl=\'%s\' WHERE name=\'%s\';' % (start, source_name)
        self._execute(sql)

    def get_file(self, source_name, filepath, filename):

        path = urllib.quote_plus(filepath)
        filename = urllib.quote_plus(filename)
        sql = 'SELECT * FROM \"files_%s\" WHERE filepath = ' % source_name
        sql += '%s AND filename = %s;'

        results = self._pool.fetchone(sql, (path, filename))
        return results

    def get_directory(self, source_name, path):
        sql = 'SELECT * from \"files_%s\" WHERE filepath = ' % source_name
        sql += '%s;'

        data = []

        results = self._pool.fetchall(sql, [urllib.quote_plus(path)])

        for r in results:
            filename=unicode(r[1], 'utf8')
            filepath=unicode(r[3], 'utf8')

            df = DiscoveredFile(
                host_name=source_name,
                path=filepath,
                name=filename,
                isdir=r[0],
                size=r[2],
                modified=r[4],
                perm=r[5],
                fileformat=r[9],
                fileext=r[8],
                fileadded=r[7]
            )
            dom = DataObjectManipulation()
            df = dom.humanize(df, humansizes=True, humandates=True, humanfile=True, humanpath=True)
            data.append(df)

        return data

    def _execute(self, sql, params=None):
        try:
            return self._pool.execute(sql, params)
        except Exception as ex:
            return Debug('Could not execute SQL command: %s\n--\n%s--' % (sql ,str(ex)), warning=True)