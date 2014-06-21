sandexer
========
A lightweight file indexer for indexing files from multiple hosts, over multiple protocols.

Lightweight in the sense that it runs fine on suboptimal hardware, sandexer is designed to run on machines ranging from raspberry-pi's to your latest Xeon box.

This application is still early in development and thus not functional yet.

![bla](http://imgur.com/cdRb50V.png)

Status: pre-alpha

Installation
===================================================
    ~$ sudo apt-get install virtualenv git postgresql postgresql-client postgresql-server-dev-X.Y
    ~$ cd ~/
    ~$ virtualenv sandexer
    ~$ cd $_
    ~$ source bin/activate
    ~$ git clone https://github.com/skftn/sandexer.git
    ~$ mv sanderex src
    ~$ pip install -r src/requirements.txt
    --
    This will fail for bottle-flash. Fix: pip install --no-install bottle-flash; touch build/bottle-flash/README.rst;pip install --no-download bottle-flash
    --
    ~$ cp conf/config.example conf/config
    ~$ vim config.py
    --Edit the config, follow instructions--
    ~$ chmod +x server.py
    ~$ python server.py
