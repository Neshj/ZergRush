# -*- coding: utf-8 -*-
import EventDrivenThread
from exploits import exploits_list
from exploits.reporter import *
from ServerLauncher import RoboServer

QUEUE_SIZE = 10
EVT_ID_START = 1
EVT_ID_STOP = 2
EVT_ID_START_GAME = 3
EVT_ID_TERMINATE_GAME = 4
EVT_ID_SEND_EXPLOIT = 5

class MainStageThread (EventDrivenThread.EventDrivenThread):
        
    def __init__(self, threadID, name):
        EventDrivenThread.EventDrivenThread.__init__(self,threadID,name,QUEUE_SIZE)
        
        self.BindEvent(EVT_ID_START, self.OnStart)
        self.BindEvent(EVT_ID_STOP, self.OnStop)
        self.BindEvent(EVT_ID_START_GAME, self.OnStartGame)
        self.BindEvent(EVT_ID_TERMINATE_GAME, self.OnTerminateGame)
        self.BindEvent(EVT_ID_SEND_EXPLOIT, self.OnSendExlpoit)
        
        self.servers = []
        
    def OnStart(self,event_data):
        print ("MainStageThread::OnStart, data = " + event_data)

        self.bl_object = event_data
    
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

    # event_data = exploit_id
    def OnSendExlpoit(self,event_data):
        print ("MainStageThread::OnSendExploit, data = " + event_data)

        exploit_id = event_data
        reporter = reporter_init()

        exploit_class = EXPLOITS[exploit_id]
        exploits = []

        # Run exploit against all teams in game
        for team in self.current_game_config:
            print "calling exploit '%s' on %s!" % (exploit_id, team["name"])
            exploit = exploit_class(team)
            exploit.run()

            exploits.append((exploit, team))

        results = []

        for i in xrange(2):
            results.append(reporter_wait(reporter))

        for exploit, team in exploits:
            for report in results:
                if team["ip"] == report[0]:
                    score = exploit.score(report[1])

                    # Update scores with result form exploit
                    scores = list(self.bl_object.GetSavedScores())
                    scores[int(team["id"]) - 1] += score
                    self.bl_object.SaveScores(scores)

                    print "%s's score for the exploit: %s" % (team["name"], score)
                    # TODO: Add the [score] to [team]

        
        
        