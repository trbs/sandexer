import sqlalchemy as sql
from sqlalchemy import or_
import bottle_sqlalchemy as sqlalchemy
from sqlalchemy import create_engine, Column, Sequence
from sqlalchemy.ext.declarative import declarative_base
import psycopg2, random, urllib, os
from bin.utils import isInt, gen_string
from dataobjects import Debug

from datetime import datetime

from gevent import monkey
monkey.patch_all()
from psycogreen.gevent import patch_psycopg
patch_psycopg()

Base = declarative_base()

class Postgres():
    def __init__(self, cfg, app):
        self._cfg = cfg
        self._db_host = self._cfg.get('Postgres', 'host')
        self._db_port = self._cfg.get('Postgres', 'port')
        self._db_database = self._cfg.get('Postgres', 'db')
        self._db_user = self._cfg.get('Postgres', 'user')
        self._db_pass = self._cfg.get('Postgres', 'pass')

        self.engine = create_engine('postgresql+psycopg2://%s:%s@%s:%s/%s' % (
            self._db_user,
            self._db_pass,
            self._db_host,
            self._db_port,
            self._db_database), echo=False
        )

        self.plugin = sqlalchemy.Plugin(
            self.engine, # SQLAlchemy engine created with create_engine function.
            Base.metadata, # SQLAlchemy metadata, required only if create=True.
            keyword='db', # Keyword used to inject session database in a route (default 'db').
            create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
            commit=False, # If it is true, plugin commit changes after route is executed (default True).
            use_kwargs=False # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
        )

        app.install(self.plugin)

    def bulk_add(self, db, files, source_name):
        # Everything in here should be save from sqli as long
        # as source_name is alphanummeric

        start = datetime.now()
        temp = '/tmp/%s.crawl' % gen_string(random.randrange(5,12))

        conn = psycopg2.connect('host=%s port=%s dbname=%s user=%s password=%s' % (
            self._cfg.get('Postgres', 'host'),
            self._cfg.get('Postgres', 'port'),
            self._cfg.get('Postgres', 'db'),
            self._cfg.get('Postgres', 'user'),
            self._cfg.get('Postgres', 'pass')))

        f = open(temp, 'w')

        inserts = 0
        total_size = 0
        total_files = 0
        filedistribution = [0, 0, 0, 0, 0]
        id = 0

        cur = conn.cursor()
        sql = 'DELETE FROM files WHERE source_name = \'%s\'' % source_name
        cur.execute(sql)
        conn.commit()

        sql = 'SELECT id from \"files\" order by id desc limit 1;'
        cur.execute(sql)
        rows = cur.fetchone()

        if rows:
            id = rows[0] + 1

        for df in files:
            isdir = str(df.isdir).upper()

            df.filename = urllib.quote_plus(df.filename) if df.filename else None
            df.filepath = urllib.quote_plus(df.filepath) if df.filepath else None
            df.fileext = urllib.quote_plus(df.fileext) if df.fileext else None
            setattr(df, 'filename_low', df.filename.lower() if df.filename else None)
            setattr(df, 'filepath_low', df.filepath.lower() if df.filepath else None)

            line = '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (
                str(id),
                source_name,
                isdir,
                df.filename,
                df.filename_low,
                df.filepath_low,
                df.filesize,
                df.filepath,
                df.filemodified,
                df.fileperm,
                df.fileadded,
                df.fileext,
                df.fileformat, str(0)
            )

            f.write(line)

            inserts += 1
            if df.filesize:
                total_size += df.filesize if df.filesize != 4096 else 0

            if not df.isdir and '.' in df.filename:
                filedistribution[df.fileformat] += 1
                total_files += 1

            id += 1
        f.close()

        # to-do
        # 1. https://pythonhosted.org/psycopg2/cursor.html#cursor.copy_expert
        #    should work without having to use postgres superuser privs
        cur = conn.cursor()
        try:
            sql = 'COPY \"files\" FROM \'%s\' DELIMITER \'|\' NULL \'None\';' % (temp)

            cur.execute(sql)

        except Exception as e:
            e = 'e'

        os.remove(temp)
        end = datetime.now()
        Debug('Source %s - %s seconds for %s item INSERTS' % (source_name, str((end - start).total_seconds()),inserts), info=True)

        # Update the total size of the indexed Source
        sql = 'UPDATE source SET total_size=%s where name=\'%s\';' % (total_size, source_name)
        cur.execute(sql)

        # Update the total amount of files of the indexed source
        sql = 'UPDATE source SET total_files=%s where name=\'%s\';' % (total_files, source_name)
        cur.execute(sql)

        # Update the distribution of files
        sql = '''
                UPDATE source SET (
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

        cur.execute(sql)

        # Update the last crawled time
        sql = 'UPDATE source SET crawl_lastcrawl=\'%s\' WHERE name=\'%s\';' % (start, source_name)
        cur.execute(sql)
        conn.commit()
        end = datetime.now()
        print 'TOTAL: ' + str((end - start).total_seconds()) + ' seconds'

        db.expire_all()

class SourceFile(Base):
    """Represents a file or directory"""
    # if this shit gets out of control look into table partitioning
    __tablename__ = 'files'

    id = Column(sql.Integer, Sequence('id_seq'), primary_key=True)

    source_name = Column(sql.String())
    is_directory = Column(sql.Boolean())
    filename = Column(sql.String())
    filename_low = Column(sql.String())
    filepath_low = Column(sql.String())
    filesize = Column(sql.BigInteger())
    filepath = Column(sql.String())
    filemodified = Column(sql.DateTime())
    fileperm = Column(sql.Integer())
    fileadded = Column(sql.DateTime())
    fileext = Column(sql.String())
    fileformat = Column(sql.Integer())
    download_count = Column(sql.BigInteger())

    def __init__(self, source_name, path, name, isdir, size=None, modified=None, perm=None, fileformat=None, fileext=None, fileadded=None):
        self.source_name = source_name
        self.filepath = path
        self.filename = name
        self.filepath_low = self.filepath.lower() if self.filepath else None
        self.filename_low = self.filename.lower() if self.filename else None
        self.filesize = int(size) if isInt(size) else size
        self.isdir = isdir
        self.filemodified = modified
        self.fileperm = int(perm) if isInt(perm) else perm
        self.fileformat = fileformat
        self.fileext = fileext
        self.fileadded = fileadded
        self.url_icon = None

class Source(Base):
    """Represents a source"""
    __tablename__ = 'source'
    id = Column(sql.Integer, Sequence('id_seq'), primary_key=True)

    name = Column(sql.String())
    description = Column(sql.String())
    added = Column(sql.DateTime())
    crawl_url = Column(sql.String())
    crawl_protocol = Column(sql.String())
    crawl_username = Column(sql.String())
    crawl_password = Column(sql.String())
    crawl_authtype = Column(sql.String())
    crawl_interval = Column(sql.String())
    crawl_useragent = Column(sql.String())
    crawl_verifyssl = Column(sql.Boolean())
    crawl_lastcrawl = Column(sql.DateTime())
    crawl_wait = Column(sql.Integer())
    filetypes = Column(sql.String())
    bandwidth = Column(sql.Integer())
    color = Column(sql.Integer())
    country = Column(sql.String())
    thumbnail_url = Column(sql.String())
    filedistribution_files = Column(sql.Integer())
    filedistribution_documents = Column(sql.Integer())
    filedistribution_movies = Column(sql.Integer())
    filedistribution_music = Column(sql.Integer())
    filedistribution_pictures = Column(sql.Integer())
    filetypes = Column(sql.String())
    total_size = Column(sql.BigInteger())
    total_files = Column(sql.BigInteger())
    tags = Column(sql.String())
    html_header = Column(sql.String())

    def __init__(self):
        self.name = None
        self.description = None
        self.added = datetime.now()
        self.crawl_url = None
        self.crawl_protocol = None
        self.crawl_username = None
        self.crawl_password = None
        self.crawl_authtype = None
        self.crawl_interval = None
        self.crawl_useragent = None
        self.crawl_verifyssl = None
        self.crawl_lastcrawl = None
        self.crawl_wait = -1
        self.filetypes = []
        self.bandwidth = -1
        self.color = -1
        self.total_size = 0
        self.total_files = 0
        self.thumbnail_url = '/static/images/source_default_thumbnail.png'
        self.country = None
        self.filedistribution = {}
        self.filedistribution_files = 0
        self.filedistribution_documents = 0
        self.filedistribution_movies = 0
        self.filedistribution_music = 0
        self.filedistribution_pictures = 0
        self.tags = None
        self.html_header = None

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)

        return d

    def calc_filedistribution(self):
        """Calculates the distribution of files"""
        def _calc(inp):
            if self.total_files:
                pct = round(100 * round(inp) / self.total_files, 2)
                return pct if pct >= 1 else 0
            else:
                return 0

        self.filedistribution = {
            'files': _calc(self.filedistribution_files),
            'documents': _calc(self.filedistribution_documents),
            'movies': _calc(self.filedistribution_movies),
            'music': _calc(self.filedistribution_music),
            'pictures': _calc(self.filedistribution_pictures)
        }