import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger('app.server')

formatter = logging.Formatter("%(asctime)s  %(levelname)-8s  %(module)-10s  %(message)s")
formatter_stream = logging.Formatter("%(levelname)-8s  %(message)s ")

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')
fh = TimedRotatingFileHandler(PATH, when='midnight', backupCount='3', encoding='utf-8')

fh.setFormatter(formatter)

sh = logging.StreamHandler(sys.stderr)
sh.setFormatter(formatter_stream)
sh.setLevel(logging.ERROR)

log.addHandler(fh)
log.addHandler(sh)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    log.error('System message')
