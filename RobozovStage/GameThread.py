# -*- coding: utf-8 -*-
import LogicThread
import time

class GameThread (LogicThread.LogicThread):
    def __init__(self, threadID, name):
        LogicThread.LogicThread.__init__(self,threadID,name)
        
    # Override
    def HandleEvent(self):
        print ("In GameThread::HandleEvent")
        time.sleep(1)
