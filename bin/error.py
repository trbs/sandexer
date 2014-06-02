from datetime import datetime
import logging
import inspect

class Error():
    def __init__(self, message, data=None):
        try:
            self.caller = inspect.stack()[1][0].f_locals.get('self', None).__class__.__name__
        except:
            self.caller = '?'

        self.now = datetime.now()
        self.message = message
        self.data = data
        logging.error('class:%s - %s' % (self.caller,message))