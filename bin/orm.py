import sqlalchemy as sql
import bottle_sqlalchemy as sqlalchemy
from sqlalchemy import create_engine, Column, Sequence
from sqlalchemy.ext.declarative import declarative_base
from bin.utils import isInt
from dataobjects import DataObjectManipulation

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
            self._db_database), echo=True
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

class SourceFile(Base):
    """Represents a file or directory"""
    # if this shit gets out of control look into table partitioning
    __tablename__ = 'files'

    id = Column(sql.Integer, Sequence('id_seq'), primary_key=True)

    source_name = Column(sql.String())
    is_directory = Column(sql.Boolean())
    filename = Column(sql.String())
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