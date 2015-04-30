# -*- coding: utf-8 -*-

# Amir Krayden
# 26/04/14

import LogicThread
import threading
import Queue


class EventDrivenThread (LogicThread.LogicThread):
    def __init__(self, threadID, name, queueSize):
        LogicThread.LogicThread.__init__(self,threadID,name)
        
        # Message Queue
        self.queueLock = threading.Lock()
        self.workQueue = Queue.Queue(queueSize)
        self.bind_events = {}
    
    # Bind event
    def BindEvent(self,event_id,event_handler):
        self.bind_events[event_id] = event_handler
    
    # Post Event
    def PostEvent(self, event_id,event_data):
        self.queueLock.acquire()
        self.workQueue.put((event_id, event_data))
        self.queueLock.release()
        
    # Override
    def HandleEvent(self):
        self.queueLock.acquire()
        
        if not self.workQueue.empty():
            event_id, event_data = self.workQueue.get()
            
            if (self.bind_events[event_id] != None):
                event_handler = self.bind_events[event_id] 
                event_handler(event_data)
            
        self.queueLock.release()
    