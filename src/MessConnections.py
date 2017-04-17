import MagicStrings
import MessLogger
import MessConfigManager
from sqlalchemy import create_engine
import os

class MessConnections: 
  def __init__(self):
    self.conf = MessConfigManager.MessConfigManager()
    self.logger = MessLogger.GetLogger()

  def sqlConnect(self):
    #print (self.user, self.host, self.port, self.pw)
    user = self.conf.getConfDict()["CONFIGsql"]["username"]
    host = self.conf.getConfDict()["CONFIGsql"]["host"]
    port = self.conf.getConfDict()["CONFIGsql"]["port"]
    pw = self.conf.getConfDict()["CONFIGsql"]["password"]
    dbname = self.conf.getConfDict()["CONFIGsql"]["dbname"]
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, pw, host, port,dbname)
    engine = create_engine(url)
    try:
      conn = engine.connect()
    except Exception as e:
       self.logger.exception( e)
       return None
    return conn