# -*- coding: utf-8 -*-
import EventDrivenThread
from ServerLauncher import RoboServer

QUEUE_SIZE = 10
EVT_ID_START = 1
EVT_ID_STOP = 2
EVT_ID_START_GAME = 3
EVT_ID_TERMINATE_GAME = 4

class MainStageThread (EventDrivenThread.EventDrivenThread):
        
    def __init__(self, threadID, name):
        EventDrivenThread.EventDrivenThread.__init__(self,threadID,name,QUEUE_SIZE)
        
        self.BindEvent(EVT_ID_START, self.OnStart)
        self.BindEvent(EVT_ID_STOP, self.OnStop)
        self.BindEvent(EVT_ID_START_GAME, self.OnStartGame)
        self.BindEvent(EVT_ID_TERMINATE_GAME, self.OnTerminateGame)
        
        self.servers = []
        
    def OnStart(self,event_data):
        print ("MainStageThread::OnStart, data = " + event_data)
    
    def OnStop(self,event_data):
        print ("MainStageThread::OnStop, data = " + event_data)

    def OnStartGame(self,event_data):
        print ("MainStageThread::OnStartGame, data = ", event_data)
        
        # reset running servers list
        self.running_servers = []
        
        # build a server for each team
        for team_config in event_data: 
            server = RoboServer(team_config['name'], \
				                team_config['Remote_ip'], \
                                team_config['Robot_ip'], \
                                team_config['server_remote_port'], \
                                team_config['server_robot_port'])
            
            # add to running servers
            self.running_servers.append(server)
            
            # launch!
            server.Launch()
        
    def OnTerminateGame(self,event_data):
        # send terminate to all running servers
        for server in self.running_servers:
            server.Terminate()
            
