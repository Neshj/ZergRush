#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Amir Krayden
#   18/04/15
#

from MainFrame import MainFrame
from wx import wx
import os
from RobozovConfigLoader import RobozovConfigLoader
import GameThread
import MainStageThread
import cPickle as pickle
from Tournament import TournamentUtility


class RobozovStageMain:

    def __init__(self):
        print ("RobozovMain init")

        self._config_file_name = "RobozovArenaConfig.xml"

        
    # Load configuration
    def LoadConfig(self):
        print ("RobozovMain load config")

        config_loader = RobozovConfigLoader(self._config_file_name)
        self.config = config_loader.getConfig()
        print ("Configuration is:")
        data = self.config.getConfigData()
        print (data)
        print (len(data["Teams"]))

        self.LoadDataBase()

    def ShowUI(self):
        app = wx.App(redirect=False)   # Error messages go to popup window
        self.top = MainFrame("<<Robozov Stage>>",self)

        # Start threads
        self.StartThreads()

        self.top.Show()
        app.MainLoop()
        print ("UI closed")

        # Close threads
        self.CloseThreads()
        print ("Main thread is done")

        print ("Database was saved")

    def StartThreads(self):
        print ("Starting Threads")

        self.threads = []

        self.main_stage_thread = MainStageThread.MainStageThread(1,"MainLogicThread")
        self.threads.append(self.main_stage_thread)

        self.game_thread = GameThread.GameThread(2,"GameThread")
        self.threads.append(self.game_thread)

        for t in self.threads:
            t.start()

        self.main_stage_thread.PostEvent(MainStageThread.EVT_ID_START, self)

    def CloseThreads(self):
        print ("Closing Threads")

        for t in self.threads:
            t.CloseThread()
            t.join()

        print ("All threads finished")

    # Business Logic functions
    def LoadDataBase(self):
        
        try:
            self.saved_scores = pickle.load(open( "/home/yusuf/ZergRush/RobozovStage/scores", "r" ))
        except IOError as e:
            self.saved_scores = []
            print (e)
            
        print ("Database loaded")
        print (self.saved_scores)

    def SaveScoresCallBack(self,scores_list):
        self.top.SaveScores(scores_list)
    
    def SaveScores(self,scores_list,update_ui):
        # [0] = team_id
        # [1] = team_name
        # [2] = team_score
        
        self.saved_scores = list(scores_list)
        print (self.saved_scores)
        
        if update_ui == True:
            self.top.UpdateScoresList()

        self.SaveDataBase()
        
    def SaveDataBase(self):
        pickle.dump( self.config, open( "config_save.p", "wb" ) )
        
        if os.path.exists("/home/yusuf/ZergRush/RobozovStage/scores"):
            os.unlink("/home/yusuf/ZergRush/RobozovStage/scores")
            
        f = open("/home/yusuf/ZergRush/RobozovStage/scores", "w")
        pickle.dump(self.saved_scores, f)
        f.close()
        
        print ("db saved")

    def GetConfig(self):
        return (self.config.getConfigData())

    def GetSavedScores(self):
        return (self.saved_scores)

    def NewTournament(self):
        self.match_list = TournamentUtility().GenerateTournament(self.config.getConfigData())
        print (self.match_list)
        print (len(self.match_list))
        return self.match_list

    def StartNewGame(self,match_tup):
        print "Starting New Game!"
        print (match_tup)

        # parse tuple to get team id's
        teams_in_play = []
        teams_in_play.append((int)(match_tup[0])) # 1st team id
        teams_in_play.append((int)(match_tup[2])) # 2nd team id

        # collect teams configuration for launching their servers
        teams_config = []
        for team in teams_in_play:
            print "Team #%d is playing!" % team
            teams_config.append(self.config.getConfigData()["Teams"][team - 1]) # team - 1 => team number to list index

        self.current_game_config = teams_config
        
        self.main_stage_thread.PostEvent(MainStageThread.EVT_ID_START_GAME, teams_config)

    def SendExploit(self,exploit_data):
        self.main_stage_thread.PostEvent(MainStageThread.EVT_ID_SEND_EXPLOIT, exploit_data)
    
    def GetCurrentGameConfig(self):
        return (self.current_game_config)

    def TerminateGame(self):
        print "Terminating Current Game!"
        self.main_stage_thread.PostEvent(MainStageThread.EVT_ID_TERMINATE_GAME, "Stop the game!")
