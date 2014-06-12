import sys
import os
import string
import random
from datetime import datetime
import logging
import inspect


def bytesTo(bytes, to, bsize=1024):
    r = float(bytes)
    for i in range({'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }[to]):
        r = r / bsize
    return(r)

def isInt(num):
    try:
        a = int(num)
        return True
    except:
        return False

def generate_string(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Debug():
    def __init__(self, message, data=None, warning=False, info=False):
        try:
            self.caller = inspect.stack()[1][0].f_locals.get('self', None).__class__.__name__
        except:
            self.caller = '?'

        self._log = logging.getLogger('file_logger')
        self.now = datetime.now()
        self.message = message
        self.data = data

        msg = 'class:%s:{{TYPE}} - %s' % (self.caller,message)
        date = self.now.strftime('%d %b %Y %H:%M:%S')

        if warning:
            self._log.warning('%s:%s' % (date,msg.replace('{{TYPE}}', 'WARNING')))
        elif info:
            self._log.info('%s:%s' % (date,msg.replace('{{TYPE}}', 'INFO')))
        else:
            self._log.error('%s:%s' % (date,msg.replace('{{TYPE}}', 'ERROR')))