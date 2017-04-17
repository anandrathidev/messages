# Read configuration file from config 

import json
import MagicStrings

class MessConfigManager:
  def __init__(self):
    self.gconf = None
    try:
      confPath  = MagicStrings.MAGICVARIABLES.CPATH
      with open(confPath) as json_data:
        self.gconf = json.load(json_data)
    except Exception as e:
      raise e

  def GetConfig(self, key):
    return self.gconf.get(key)

  def getConfDict(self):
    return self.gconf