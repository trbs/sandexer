sandexer
========
A lightweight file indexer for indexing files from multiple hosts, over multiple protocols.

Lightweight in the sense that it runs fine on suboptimal hardware, sandexer is designed to run on machines ranging from raspberry-pi's to your latest Xeon box.

Features:
- Crawling HTTP open directories (webdav)(BASIC/DIGEST)
- Crawling FTP/SMB servers
- Automatic crawling at intervals
- Dynamically caching of directories + precaching
- The creation of users and group. Determine which group sees which server.
- PostgreSQL/SQLite/MySQL/Oracle/Sybase/MsSQL/Firebird/Drizzle
- Bootstrap 3.0 interface with an admin panel.

Requirements:
- python 2.* on linux

This application is still early in development and thus not functional yet.

![bla](http://imgur.com/cdRb50V.png)

![bla2](http://imgur.com/7pdGXe9.png)

Status: pre-alpha

Installation
===================================================
    ~$ sudo apt-get install virtualenv git libjpeg-dev postgresql postgresql-client postgresql-server-dev-X.Y
    ~$ cd ~/
    ~$ virtualenv sandexer
    ~$ cd $_
    ~$ source bin/activate
    ~$ git clone https://github.com/skftn/sandexer.git
    ~$ mv sanderex src
    ~$ pip install -r src/requirements.txt
    ~$ cp conf/config.example conf/config
    ~$ vim config.py
    --Edit the config, follow instructions--
    ~$ chmod +x server.py
    ~$ python server.py
