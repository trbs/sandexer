sandexer
========
A lightweight file indexer for indexing files from multiple hosts, over multiple protocols.

Lightweight in the sense that it runs fine on suboptimal hardware, sandexer is designed to run on machines ranging from raspberry-pi's to your latest Xeon box.

This application is still early in development and thus not functional yet.


Installation
===================================================
    ~$ sudo apt-get install virtualenv git postgresql postgresql-client postgresql-server-dev-X.Y
    ~$ cd ~/
    ~$ virtualenv sandexer
    ~$ cd $_
    ~$ source bin/activate
    ~$ git clone https://github.com/skftn/sandexer.git
    ~$ mv sanderex src
    ~$ cd $_
    ~$ pip install -r requirements
    ~$ cp conf/config.example conf/config
    ~$ vim config.py
    --Edit the config, follow instructions--
    ~$ chmod +x server.py
    ~$ python server.py