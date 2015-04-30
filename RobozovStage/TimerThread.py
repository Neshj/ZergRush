# -*- coding: utf-8 -*-
import LogicThread
import time

class TimerThread (LogicThread.LogicThread):
    def __init__(self, threadID, name, callback_obj):
        LogicThread.LogicThread.__init__(self,threadID,name)
        
        self.callback_obj = callback_obj
        
    # Override
    def HandleEvent(self):
        self.callback_obj.UpdateTimeCallback()
        time.sleep(1)