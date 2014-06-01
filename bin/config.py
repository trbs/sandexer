import ConfigParser
import os
import logging

class Config():
    def __init__(self):
        self._last_accessed = None
        self._app_root = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

        self._items = {}

    def reload(self):
        try:
            cfg_file = '%s/conf/config' % self._app_root
            if not os.path.isfile(cfg_file):
                raise Exception

            cfg = ConfigParser.ConfigParser()
            cfg.read(cfg_file)

            data = {}
            for section in cfg.sections():
                data[section] = {}

                for k,v in cfg.items(section):
                    try:
                        data[section][k] = int(v)
                    except:
                        data[section][k] = v

            self._items = data
            return True
        except:
            logging.warning('Could not load config file \'%s/conf/config\'' % self._app_root)
            return False

    def get(self, section, item):
        try:
            return self._items[section][item]
        except:
            logging.warning('Could not access config variable \'%s\' from section \'%s\'' % (item, section))
            return None