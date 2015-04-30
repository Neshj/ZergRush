# -*- coding: utf-8 -*-

import xml.etree.ElementTree as etree
from RobozovArenaConfig import *

class RobozovConfigLoader:

    def __init__(self,config_file_name):
        self._file_name = config_file_name

    def getConfig(self):

        config = RobozovArenaConfig()

        tree = etree.parse(self._file_name)
        root = tree.getroot()

        # parse all nodes
        self.parseNodes(root,config)

        return (config)

    def parseNodes(self,root,config):

        # parse all nodes
        for child in root:

            if (child.tag != "Teams"):
                print (child.attrib)
                config.config_data[child.tag] = child.attrib
            else:
                # get each team
                i = 1
                for team in child:
                    config.config_data[child.tag].append(team.attrib)
                    i += 1
