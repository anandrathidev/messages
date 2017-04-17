# initialise logger and specify configuration

import logging
import MagicStrings
import os
from logging.handlers import RotatingFileHandler

logger = None

def GetLogger():
  import datetime
  global logger 
  if logger==None:
    logger = logging.getLogger('mess')
    if (len(logger.handlers) == 0): 
      spid = str(os.getpid())
      date = datetime.datetime.now().strftime('%Y-%m-%d')
      logPath  = '/var/log/webmess/webmess_log_' + str(date) + '.log'
      hdlr = RotatingFileHandler(filename = logPath , mode='a', maxBytes = 5*1024*1024)
      formatter = logging.Formatter('%(process)d  %(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
      hdlr.setFormatter(formatter)
      logger.addHandler(hdlr)
      logger.setLevel(logging.INFO)
  return logger