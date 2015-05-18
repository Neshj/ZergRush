#!/usr/bin/python
# -*- coding: <<encoding>> -*-
#-------------------------------------------------------------------------------
#   <<project>>
#
#-------------------------------------------------------------------------------
from socket import *
import wxversion
from TimerThread import TimerThread
wxversion.select("2.8")
import wx.html
import sys
from datetime import datetime

import wx.lib.newevent as NE

from GameFrame import GameFrame

TimerEvent, EVT_TIMER_CALLBACK = NE.NewEvent()
GameEvent, EVT_GAME_CALLBACK = NE.NewEvent()

aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>"""


ID_SPLITTER=300
ID_SPLITTER1=301
ID_SPLITTER2=302
LIST_FONT_SIZE = 10

EVT_OK = 82

GAME_TIME = 90
EVT_START = 20
EVT_STOP = 21
EVT_ATTACK = 22

EVT_TEAM1_PLUS = 30
EVT_TEAM1_MINUS = 31
EVT_TEAM2_PLUS = 32
EVT_TEAM2_MINUS = 33


filenames = ["Graphics/Robotzov_Text.png", "Graphics/Robotzov2_TextB.png"]

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class AboutBox(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, -1, "About <<project>>",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
                wx.TAB_TRAVERSAL)
        hwin = HtmlWindow(self, -1, size=(400,200))
        vers = {}
        vers["python"] = sys.version.split()[0]
        vers["wxpy"] = wx.VERSION_STRING
        hwin.SetPage(aboutText % vers)
        irep = hwin.GetInternalRepresentation()
        hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
        self.SetClientSize(hwin.GetSize())
        self.CentreOnParent(wx.BOTH)
        self.SetFocus()

class NewGameFrame(wx.Frame):
    def __init__(self, title, bl_object):
        self.bl_object = bl_object
        
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,200))
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Get the Current game config
        # self.current_game_config = self.bl_object.GetCurrentGameConfig()
        
        team_names = []
        for team in self.bl_object.GetConfig()["Teams"]:
            #team = self.bl_object.GetConfig()[team_index]
            team_names.append(team['name'])

        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(50)
        
        self.team_1_combo =  wx.ComboBox(self.splitter, -1,choices=team_names, style=wx.CB_READONLY)
        self.team_2_combo =  wx.ComboBox(self.splitter, -1,choices=team_names, style=wx.CB_READONLY)
        self.ok_button = wx.Button(self, EVT_OK, 'OK')
        self.ok_button.Bind(wx.EVT_BUTTON, self.OnOK, id=EVT_OK)
        self.splitter.SplitVertically(self.team_1_combo, self.team_2_combo)
        #vbox.Add(self.team_1_combo,1,wx.ALIGN_CENTER)
        #vbox.Add(self.team_2_combo,1,wx.ALIGN_CENTER)
        
        vbox.Add(self.splitter,1,wx.ALIGN_CENTER)
        vbox.Add(self.ok_button,1,wx.ALIGN_CENTER)

        self.SetSizer(vbox)
        
        self.SetSize((400, 100))
                       
    def OnOK(self, event):
        team_1 = self.bl_object.GetConfig()["Teams"][self.team_1_combo.GetSelection()]
        team_2 = self.bl_object.GetConfig()["Teams"][self.team_2_combo.GetSelection()]
        match_tup = (team_1["id"], team_1["name"], team_2["id"], team_2["name"], "0")
        p = self.parent_window
        p.match_list.append(match_tup)
        p.AddMatchData(len(p.match_list), match_tup)

        # Color the current game red
        p.p2.Select(p.current_game, True)
        item = p.p2.GetFirstSelected()
        p.p2.SetItemBackgroundColour(item, "Red")
        p.p2.Select(p.current_game, False)

        self.bl_object.StartNewGame(match_tup)

        game_frame = GameFrame("<<Robozov Stage>>",self.bl_object)
        game_frame.Show()

        p.current_game += 1


    def OnStartGame(self,event):
        self.UpdateGameLabel()
        self.Bind(EVT_TIMER_CALLBACK,self.OnTimerCallback)
        self.Bind(EVT_GAME_CALLBACK,self.OnGameEventCallback)
        
        self.time_thread = TimerThread(-1,"",self)
        self.time_thread.start() # after 1 second, the callback function will be called
        self.current_game = 0

    def OnCyberAttack(self,event):
        print ("Attack")
        ExploitsDialog(self, -1, 'Exploits Cyber Attack',self.bl_object).Show()
        
    def OnStopGame(self,event):
        print ("Stopping Game")
        self.bl_object.TerminateGame()
        try:
            self.time_thread.CloseThread()
        except AttributeError:
            print ("time thread does not exits")


    def ResetTeamsList(self):
        pass
        #self.p1.ClearAll()
        #self.p1.InsertColumn(0, 'From', width=100)
        #self.p1.InsertColumn(1, 'To', width=100)
        #self.p1.InsertColumn(2, 'Current message', wx.LIST_FORMAT_RIGHT, 250)
        
        #self.p2.ClearAll()
        #self.p2.InsertColumn(0, 'From', width=100)
        #self.p2.InsertColumn(1, 'To', width=100)
        #self.p2.InsertColumn(2, 'Current message', wx.LIST_FORMAT_RIGHT, 250)

    def UpdateTeamsList(self):
        # Build a tuple for each team
        teams = self.config_data['Teams']

        for team in teams:
            team_tup = (team['id'], team['name'], '0')
            self.AddTeamData(team_tup)

    def AddTeamData(self,team_data):
        #index = self.p1.InsertStringItem(sys.maxint, team_data[0])
        #self.p1.SetStringItem(index, 1, team_data[1])
        #self.p1.SetStringItem(index, 2, team_data[2])
        pass


    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            try:
                self.time_thread.CloseThread()
            except AttributeError:
                print ("time thread does not exits")
                
            self.Destroy()

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnTimerCallback(self, event):
        str_time = datetime.now().strftime('%H:%M:%S')
        self.statusbar.SetStatusText(str_time + " : " + self.stage_status)
        self.s.send("Tick")

        self.time_left -= 1;
        
        if self.time_left < 0:
        	self.time_thread.CloseThread()
        	return
        
        # Update the game label
        self.UpdateGameLabel()
        
        # Update the progressbar
        self.UpdateProgressBar()

    def OnGameEventCallback(self, event):
        print ("Game event")

    def ResetProgressBar(self):
        self.progress_count = 0
        self.progress.SetValue(self.progress_count)
        wx.Yield()

    def UpdateProgressBar(self):
        self.progress_count += 1
        self.progress.SetValue(self.progress_count)
        wx.Yield()
        
    def UpdateGameLabel(self):
        (min,sec) = divmod(self.time_left, 60)
        self.m_text_game.SetLabel("Game On! time left " + str(min) + ":" + str(sec))
        self.m_text_game.SetForegroundColour("Blue")

    def UpdateTimeCallback(self):
        #time_str = datetime.now().strftime('%H:%M:%S')
        wx.PostEvent(self,TimerEvent())

    def UpdateGameEvent(self):
        print ("Game event called")
