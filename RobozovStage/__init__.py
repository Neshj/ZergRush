#!/usr/bin/python


# -*- coding: utf-8 -*-
from RobozovStageMain import *

class RoboEntryPoint:
     
    def __init__(self):
        print ("Robozov init")

        self.main = RobozovStageMain()

    def start(self):
        self.main.LoadConfig()
        self.main.ShowUI()

if (__name__ == "__main__"):
    main = RoboEntryPoint()
    main.start()

