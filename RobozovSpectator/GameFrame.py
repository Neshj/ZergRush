#!/usr/bin/python
# -*- coding: <<encoding>> -*-
#-------------------------------------------------------------------------------
#   <<project>>
#
#-------------------------------------------------------------------------------

import wxversion
from TimerThread import TimerThread
wxversion.select("2.8")
import wx.html
import sys
from datetime import datetime

import wx.lib.newevent as NE

from Exploits import ExploitsDialog

TimerEvent, EVT_TIMER_CALLBACK = NE.NewEvent()
GameEvent, EVT_GAME_CALLBACK = NE.NewEvent()
UpdateEvent, EVT_UPDATE_CALLBACK = NE.NewEvent()

aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>"""


ID_SPLITTER=300
ID_SPLITTER2=301
LIST_FONT_SIZE = 10

GAME_TIME = 90
EVT_START = 20
EVT_STOP = 21
EVT_ATTACK = 22


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

class GameFrame(wx.Frame):
    def __init__(self, title, bl_object):
        
        # Get the Current game config
        self.current_game_config = [{"name": "Team1"},{"name": "Team2"}]
                
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,200))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.statusbar = self.CreateStatusBar()
        self.stage_status = 'Game'
        self.statusbar.SetStatusText(self.stage_status)
        self.statusbar.Show()

        self.sizer = wx.BoxSizer(wx.VERTICAL)


        img1 = wx.Image(filenames[1], wx.BITMAP_TYPE_ANY)
        w = wx.DisplaySize()[1]
        h = img1.GetHeight()
        img1 = img1.Scale(w, h/5)
        self.sb1 = wx.StaticBitmap(self, -1, wx.BitmapFromImage(img1))
        self.sizer.Add(self.sb1,flag=wx.ALIGN_CENTER, border=10)

        self.time_left = GAME_TIME
        self.m_text_game = wx.StaticText(self, -1, "Ready to Game")
        self.m_text_game.SetFont(wx.Font(22, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.m_text_game.SetForegroundColour("Blue")
        self.sizer.Add(self.m_text_game,1,flag=wx.ALIGN_CENTER)
        
        w = wx.DisplaySize()
        w = wx.Size(w[0]-100,w[1]/20)

        self.splitter_text = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER,size=w)
        self.splitter_text.SetMinimumPaneSize(0)

        self.splitter_score = wx.SplitterWindow(self, ID_SPLITTER2, style=wx.SP_BORDER,size=w)
        self.splitter_score.SetMinimumPaneSize(0)
        
        self.m_text_team_1 = wx.StaticText(self.splitter_text, -1, "Team 1: " + self.current_game_config[0]["name"],size=(w[0]/2,w[1]))
        self.m_text_team_1.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.m_text_team_1.SetForegroundColour("Black")
        
        self.m_text_score_1 = wx.StaticText(self.splitter_score, -1, "Score: 0" ,size=(w[0]/2,w[1]))
        self.m_text_score_1.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.m_text_score_1.SetForegroundColour("Black")

        #self.m_text_team_1.GetBestSize()
        
        self.m_text_team_2 = wx.StaticText(self.splitter_text, -1, "Team 2: " + self.current_game_config[1]["name"],size=(w[0]/2,w[1]))
        self.m_text_team_2.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.m_text_team_2.SetForegroundColour("Red")
        
        self.m_text_score_2 = wx.StaticText(self.splitter_score, -1, "Score: 0" ,size=(w[0]/2,w[1]))
        self.m_text_score_2.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.m_text_score_2.SetForegroundColour("Red")

        self.splitter_text.SplitVertically(self.m_text_team_1, self.m_text_team_2)
        self.splitter_score.SplitVertically(self.m_text_score_1, self.m_text_score_2)
        
        self.sizer.Add(self.splitter_text,1,flag=wx.EXPAND,border=10)
        self.sizer.Add(self.splitter_score,1,flag=wx.EXPAND,border=10)

        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(100)

        self.progress = wx.Gauge(self, -1, 90,size=w)  #create a progress bar with max 100
        self.sizer.Add(self.progress,2,wx.ALIGN_CENTRE)
        self.ResetProgressBar()
        
        self.score_team_1 = 0
        self.score_team_2 = 0

        self.SetSizer(self.sizer)
        
        size = wx.DisplaySize()
        size = (size[0], 400)
        self.SetSize(size)
        
        self.msg_event = UpdateEvent
        self.msg = ""
        self.Bind(EVT_UPDATE_CALLBACK, self.OnUpdateMsg)

        
    def OnUpdateMsg(self, event):
        print "Got message: %s" % (self.msg)
        if self.msg.startswith("Tick"):
            self.OnTimerCallback(None)
        elif self.msg.startswith("ResetTick"):
            self.time_left = GAME_TIME
            self.ResetProgressBar()
            self.score_team_1 = 0
            self.score_team_2 = 0
            self.m_text_score_1.SetLabel("Score: 0")
            self.m_text_score_2.SetLabel("Score: 0")
        elif self.msg.startswith("Team1"):
            self.m_text_team_1.SetLabel("Team1: %s" % (self.msg[len("Team1 "):]))
        elif self.msg.startswith("Team2"):
            self.m_text_team_2.SetLabel("Team2: %s" % (self.msg[len("Team2 "):]))
        elif self.msg.startswith("Score1"):
            self.score_team_1 += int(self.msg[len("Score1 "):])
            self.m_text_score_1.SetLabel("Score: %d" % self.score_team_1)
        elif self.msg.startswith("Score2"):
            self.score_team_2 += int(self.msg[len("Score2 "):])
            self.m_text_score_2.SetLabel("Score: %d" % self.score_team_2)
        
    def OnStopGame(self,event):
        print ("Stopping Game")
        self.bl_object.TerminateGame()

    def ResetTeamsList(self):
        self.p1.ClearAll()
        self.p1.InsertColumn(0, 'From', width=100)
        self.p1.InsertColumn(1, 'To', width=100)
        self.p1.InsertColumn(2, 'Current message', wx.LIST_FORMAT_RIGHT, 250)
        
        self.p2.ClearAll()
        self.p2.InsertColumn(0, 'From', width=100)
        self.p2.InsertColumn(1, 'To', width=100)
        self.p2.InsertColumn(2, 'Current message', wx.LIST_FORMAT_RIGHT, 250)

    def UpdateTeamsList(self):
        # Build a tuple for each team
        teams = self.config_data['Teams']

        for team in teams:
            team_tup = (team['id'], team['name'], '0')
            self.AddTeamData(team_tup)

    def AddTeamData(self,team_data):
        index = self.p1.InsertStringItem(sys.maxint, team_data[0])
        self.p1.SetStringItem(index, 1, team_data[1])
        self.p1.SetStringItem(index, 2, team_data[2])


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

        self.time_left -= 1;
        
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
