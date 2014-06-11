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

        self.now = datetime.now()
        self.message = message
        self.data = data

        msg = 'class:%s - %s' % (self.caller,message)

        if warning:
            logging.warning(msg)
        elif info:
            logging.info(msg)
        else:
            logging.error(msg)