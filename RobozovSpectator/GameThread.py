# -*- coding: utf-8 -*-
import LogicThread
import time
from socket import *
import wx

class GameThread (LogicThread.LogicThread):
    def __init__(self, threadID, name):
        LogicThread.LogicThread.__init__(self,threadID,name)
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.bind(("0.0.0.0", 9876))
        self.gui = None
        
    def SendToGUI(self, msg):
        if (self.gui != None):
            self.gui.msg = msg
            wx.PostEvent(self.gui, self.gui.msg_event())
        
    # Override
    def HandleEvent(self):
        print ("In GameThread::HandleEvent")
        pkt = self.s.recv(1024)
        print pkt
        self.SendToGUI(pkt)
        time.sleep(1)
