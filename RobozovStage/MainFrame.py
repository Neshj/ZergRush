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

TimerEvent, EVT_TIMER_CALLBACK = NE.NewEvent()

aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>"""

ID_TOURNAMENT_NEW=100
ID_GAME_NEW=101
ID_GAME_STOP=102
ID_TOURNAMENT_SAVE=103
ID_SPLITTER=300
ID_EXPLOITS_WINDOW=1337


LIST_FONT_SIZE = 12
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

class MainFrame(wx.Frame):
    def __init__(self, title, bl_object):

        self.bl_object = bl_object
        self.config_data = self.bl_object.GetConfig()

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,200))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        menuBar = wx.MenuBar()

        menu = wx.Menu()
        m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        menuBar.Append(menu, "&File")

        menu = wx.Menu()
        m_new_tournament = menu.Append(ID_TOURNAMENT_NEW, "New &Tournament\tAlt-T", "Start a new Tournament.")
        self.Bind(wx.EVT_MENU, self.OnNewTournament, m_new_tournament)
        m_save_tournament = menu.Append(ID_TOURNAMENT_SAVE, "&Save Tournament\tAlt-S", "Save the Tournament.")
        self.Bind(wx.EVT_MENU, self.OnSaveTournament, m_save_tournament)
        m_new_game = menu.Append(ID_GAME_NEW, "&New Game\tAlt-N", "Start a new game.")
        self.Bind(wx.EVT_MENU, self.OnNewGame, m_new_game)
        m_stop_game = menu.Append(ID_GAME_STOP, "&Stop Game\tAlt-S", "Stop the current game.")
        self.Bind(wx.EVT_MENU, self.OnStopGame, m_stop_game)

        m_exploits = menu.Append(ID_EXPLOITS_WINDOW, "&Exploits...\tAlt-E", "Send an exploit to a team...")
        self.Bind(wx.EVT_MENU, self.OnExploits, m_exploits)

        menuBar.Append(menu, "Tournament")

        menu = wx.Menu()
        m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
        menuBar.Append(menu, "&Help")
        self.SetMenuBar(menuBar)

        self.statusbar = self.CreateStatusBar()
        self.stage_status = 'Ready'
        self.statusbar.SetStatusText(self.stage_status)
        self.statusbar.Show()

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #self.m_text = wx.StaticText(self, -1, "Robozov 2 - Stage")
        #self.m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        #self.m_text.SetSize(self.m_text.GetBestSize())
        #self.sizer.Add(self.m_text,flag=wx.EXPAND|wx.CENTER|wx.TOP, border=10)

        img1 = wx.Image(filenames[1], wx.BITMAP_TYPE_ANY)
        w = wx.DisplaySize()[1]
        h = img1.GetHeight()
        img1 = img1.Scale(w, h/5)
        self.sb1 = wx.StaticBitmap(self, -1, wx.BitmapFromImage(img1))
        self.sizer.Add(self.sb1,flag=wx.ALIGN_CENTER, border=10)


        self.splitter = wx.SplitterWindow(self, ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(50)

        self.p1 = wx.ListCtrl(self.splitter, -1, style=wx.LC_REPORT)
        self.p2 = wx.ListCtrl(self.splitter, -1, style=wx.LC_REPORT)
        self.splitter.SplitVertically(self.p1, self.p2)

        font = wx.Font(pointSize=LIST_FONT_SIZE, family=wx.FONTFAMILY_DEFAULT, style=wx.NORMAL, weight=wx.FONTWEIGHT_BOLD,
               underline=False, face="", encoding=wx.FONTENCODING_DEFAULT)
        #font = self.p1.GetFont()
        self.p1.SetFont(font)
        self.p2.SetFont(font)

        # Arrange the teams list control
        self.ResetTeamsList()
        self.UpdateTeamsList()

        # Arrange the game list control
        self.ResetGameList()

        self.sizer.Add(self.splitter,1,wx.EXPAND)
        self.SetSizer(self.sizer)

        size = wx.DisplaySize()
        self.SetSize(size)

        self.Bind(EVT_TIMER_CALLBACK,self.OnTimerCallback)
        self.time_thread = TimerThread(-1,"",self)
        self.time_thread.start() # after 1 second, the callback function will be called
        self.current_game = 0

    
    def ResetTeamsList(self):
        self.p1.ClearAll()
        self.p1.InsertColumn(0, 'Team ID', width=150)
        self.p1.InsertColumn(1, 'Team Name', width=150)
        self.p1.InsertColumn(2, 'Score', wx.LIST_FORMAT_RIGHT, 100)

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

    def ResetGameList(self):
        self.p2.ClearAll()
        self.p2.InsertColumn(0, 'Game Number', width=150)
        self.p2.InsertColumn(1, 'Team 1', wx.LIST_FORMAT_RIGHT, 150)
        self.p2.InsertColumn(2, 'Team 2', wx.LIST_FORMAT_RIGHT, 150)
        self.p2.InsertColumn(3, 'Winner', wx.LIST_FORMAT_RIGHT, 100)

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.time_thread.CloseThread()
            self.Destroy()

    def OnNewGame(self,event):
        print ("New Game")
        
        # current_game = 0
        if len(self.match_list) > 0:
            match_tup = self.match_list[self.current_game]

            self.p2.Select(self.current_game, True)
            item = self.p2.GetFirstSelected()
            self.p2.SetItemBackgroundColour(item, "Red")
            self.p2.Select(self.current_game, False)

            self.bl_object.StartNewGame(match_tup)

    def OnExploits(self, event):
        print ("Exploits...")
        frame = wx.Frame(None, -1)
	c = wx.Choice(frame, -1, choices=["red", "blue", "green"])
	frame.Show()
    
    def OnStopGame(self,event):
        print ("Stopping Game")
        self.bl_object.TerminateGame()

        self.current_game += 1

    def OnNewTournament(self,event):
        print ("New Tournament")
        self.ResetGameList()
        self.match_list = self.bl_object.NewTournament()
        
        for i in range(0,len(self.match_list)):
            self.AddMatchData(i + 1, self.match_list[i])
    
    def OnSaveTournament(self,event):
        print ("Save Tournament")
        
    def AddMatchData(self,match_num,match_data):
        index = self.p2.InsertStringItem(sys.maxint, str(match_num))
        self.p2.SetStringItem(index, 1, match_data[1])
        self.p2.SetStringItem(index, 2, match_data[3])
        self.p2.SetStringItem(index, 3, match_data[4])
        

    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnTimerCallback(self, event):
        str_time = datetime.now().strftime('%H:%M:%S')
        self.statusbar.SetStatusText(str_time + " : " + self.stage_status)

    def UpdateTimeCallback(self):
        #time_str = datetime.now().strftime('%H:%M:%S')
        wx.PostEvent(self,TimerEvent())
        
        
