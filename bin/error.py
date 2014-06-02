from datetime import datetime
import logging

class Error():
    def __init__(self, message, data=None):
        self.now = datetime.now()
        self.message = message
        self.data = data
        logging.error('Error: ' + message)