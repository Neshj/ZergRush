# -*- coding: utf-8 -*-
import threading
import time

class LogicThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.exit_flag = False

    def run(self):
        # Get lock to synchronize threads
        print ("Starting thread: " + self.name)
        #threadLock.acquire()
        # Run
        while (self.exit_flag == False):
            self.HandleEvent()

        # Free lock to release next thread
        #threadLock.release()
        
    # Virtual derived function
    def HandleEvent(self):
        print ("In LogicThread::HandleEvent")
        time.sleep(1)

    def CloseThread(self):
        self.exit_flag = True
