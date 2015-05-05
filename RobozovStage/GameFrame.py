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


ID_SPLITTER=300



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

class GameFrame(wx.Frame):
    def __init__(self, title, bl_object):

        self.bl_object = bl_object
        self.config_data = self.bl_object.GetConfig()

        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(350,200))
        self.Bind(wx.EVT_CLOSE, self.OnClose)



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

        self.sizer.Add(self.splitter,1,wx.EXPAND)
        self.SetSizer(self.sizer)

        w = wx.DisplaySize()
        w = wx.Size(w[0]-100,w[1]/6)
        print ("W=" + str(w))
        self.progress = wx.Gauge(self, -1, 100,size=w)  #create a progress bar with max 100
        self.progress.SetSize(w)
        self.sizer.Add(self.progress,1)
        self.ResetProgressBar()

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



    def OnAbout(self, event):
        dlg = AboutBox()
        dlg.ShowModal()
        dlg.Destroy()

    def OnTimerCallback(self, event):
        str_time = datetime.now().strftime('%H:%M:%S')
        self.statusbar.SetStatusText(str_time + " : " + self.stage_status)

        # Update the progressbar
        self.UpdateProgressBar()

    def ResetProgressBar(self):
        self.progress_count = 0
        self.progress.SetValue(self.progress_count)
        wx.Yield()

    def UpdateProgressBar(self):
        self.progress_count += 1
        self.progress.SetValue(self.progress_count)
        wx.Yield()

    def UpdateTimeCallback(self):
        #time_str = datetime.now().strftime('%H:%M:%S')
        wx.PostEvent(self,TimerEvent())


