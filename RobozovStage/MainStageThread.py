# -*- coding: utf-8 -*-
import EventDrivenThread
from exploits.exploits_list import *
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
        print ("MainStageThread::OnStart")

        self.bl_object = event_data
    
    def OnStop(self,event_data):
        print ("MainStageThread::OnStop")

    def OnStartGame(self,event_data):
        print ("MainStageThread::OnStartGame")
        
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
        exploits = {}

        # Run exploit against all teams in game
        current_game_config = self.bl_object.GetCurrentGameConfig()
        for team in current_game_config:
            print "calling exploit '%s' on %s!" % (exploit_id, team["name"])
            exploit = exploit_class(team)
            exploit.run()

            exploits[team["Robot_ip"]] = {"team": team, "exploit": exploit}

        results = []

        for i in xrange(2):
            results.append(reporter_wait(reporter))
            
         # Update scores with result form exploit
        scores = self.bl_object.GetSavedScores()
            
        for report in results:
            if report[0] not in exploits.keys():
                continue
            
            score = exploits[report[0]]["exploit"].score(report[1])
            team = exploits[report[0]]["team"]
            
            # Update scores with result form exploit
            team_score = scores[int(team["id"]) - 1]
            scores[int(team["id"]) - 1] = (team_score[0], team_score[1], team_score[2] + score)

            exploits.pop(report[0])
            
            print "%s's score for the exploit: %s" % (team["name"], score)
        
            
        for no_report in exploits:
            score = exploits[no_report]["exploit"].score(None)
            team = exploits[no_report]["team"]
            team_score = scores[int(team["id"]) - 1]
            scores[int(team["id"]) - 1] = (team_score[0], team_score[1], team_score[2] + score)
            
            print "%s's missed! New score: %d" % (team["name"], scores[int(team["id"]) - 1][2])
            
        print scores
            
        self.bl_object.SaveScoresCallBack(scores)
 

        
        