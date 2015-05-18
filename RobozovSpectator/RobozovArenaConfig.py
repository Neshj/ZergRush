# -*- coding: utf-8 -*-

#   Amir Krayden
#   18/04/15
#

class RobozovArenaConfig:

    # Constructor
    def __init__(self):
        print("RobozovArenaConfig")

        #init members
        self.config_data = {}
        self.config_data["ArenaNetwork"] = {}
        self.config_data["ServerNetwork"] = {}
        self.config_data["RemotesNetwork"] = {}
        self.config_data["RobotsNetwork"] = {}
        self.config_data["Teams"] = []

    def getConfigData(self):
        return (self.config_data)



