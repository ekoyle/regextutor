#!/usr/bin/env python

import wx
from wx import stc
import regex_app

import os

pm_problem_filename = 'pm.dat'
sr_problem_filename = 'sr.dat'

class BasePatternMatchingPane(wx.Panel):
    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        self.pattern = regex_app.MyPatternStyledTextCtrl(self, -1)
        self.text = regex_app.MyRegexMatchCtrl(self, -1)
        self.pattern_flags = regex_app.RECheckboxes(self)
        self.pattern.AddHandler(self.text.SetRegex)
    def UpdateREFlags(self, evt):
        self.text.SetRegex( flags=self.pattern_flags.GetFlags() )
    def SetHandlers(self, frame):
        frame.Bind(stc.EVT_STC_STYLENEEDED, self.text.OnUpdate, self.text)
        frame.Bind(wx.EVT_TEXT, self.pattern.OnUpdate, self.pattern)
        frame.Bind(wx.EVT_CHAR, self.pattern.OnUpdate, self.pattern)
        self.pattern_flags.Bind(self, self.UpdateREFlags)
    def _GetPatternSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Search Pattern"), 0, 0, 0)
        my_sizer.Add(self.pattern, 0, wx.EXPAND, 0)
        return my_sizer
    def _GetOptionsSizer(self):
        my_sizer = wx.BoxSizer(wx.HORIZONTAL)
        my_sizer.Add(wx.StaticText(self, -1, "(Flags)  "), 0, 0, 0)
        self.pattern_flags.AddToSizer(my_sizer)
        return my_sizer
    def _GetTextSizer(self):
        my_sizer=wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Matched Text"), 0, 0, 0)
        my_sizer.Add(self.text, 3, wx.EXPAND, 0)
        return my_sizer
    def _GetTopSizer(self):
        return None
    def GetSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        x = self._GetTopSizer()
        if x:
            my_sizer.Add(x, 1, wx.EXPAND, 0)
        my_sizer.Add(self._GetPatternSizer(), 1, wx.EXPAND, 0)
        my_sizer.Add(self._GetOptionsSizer(), 0, 0, 0)
        my_sizer.Add(self._GetTextSizer(), 5, wx.EXPAND, 0)
        return my_sizer

class BaseSearchReplacePane(BasePatternMatchingPane):
    def __init__(self, *args, **kw):
        BasePatternMatchingPane.__init__(self, *args, **kw)
        self.replace_pattern = regex_app.MyReplacePatternStyledTextCtrl(self, -1, "")
        self.replace_text = regex_app.MyReplaceTextCtrl(self, -1)
        self.pattern.AddHandler(self.replace_text.SetRegex)
        self.replace_pattern.AddHandler(self.replace_text.SetReplace)
        self.text.AddHandler(self.replace_text.SetOriginal)
    def SetHandlers(self, frame):
        BasePatternMatchingPane.SetHandlers(self, frame)
        frame.Bind(wx.EVT_TEXT, self.replace_pattern.OnUpdate, self.replace_pattern)
        frame.Bind(wx.EVT_CHAR, self.replace_pattern.OnUpdate, self.replace_pattern)
    # FIXME: is this needed?
    #def UpdateREFlags(self, evt):
    #    BasePatternMatchingPane.UpdateREFlags(self, evt)
    #    self.replace_text.SetRegex( flags=self.pattern_flags.GetFlags() )
    def _GetReplacePatternSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Replace with"), 0, 0, 0)
        my_sizer.Add(self.replace_pattern, 0, wx.EXPAND, 0)
        return my_sizer
    def _GetReplaceTextSizer(self):
        my_sizer=wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Matched Text"), 0, 0, 0)
        my_sizer.Add(self.replace_text, 3, wx.EXPAND, 0)
        return my_sizer
    def GetSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)

        x = self._GetTopSizer()
        if x:
            my_sizer.Add(x, 1, wx.EXPAND, 0)

        patterns = wx.BoxSizer(wx.HORIZONTAL)
        patterns.Add(self._GetPatternSizer(), 1, wx.EXPAND, 0)
        patterns.Add(self._GetReplacePatternSizer(), 1, wx.EXPAND, 0)
        
        text = wx.BoxSizer(wx.HORIZONTAL)
        text.Add(self._GetTextSizer(), 1, wx.EXPAND, 0)
        text.Add(self._GetReplaceTextSizer(), 1, wx.EXPAND, 0)
        
        my_sizer.Add(patterns, 1, wx.EXPAND, 0)
        my_sizer.Add(self._GetOptionsSizer(), 0, 0, 0)
        my_sizer.Add(text, 6, wx.EXPAND, 0)
        return my_sizer

class PatternMatchingPane(BasePatternMatchingPane):
    def __init__(self, *args, **kw):
        BasePatternMatchingPane.__init__(self, *args, **kw)
        self.file_dlg = wx.FileDialog(self, "Choose File", )
        self.load_file_button = wx.Button(self, -1, "load text from file")
    def FileOpen(self, evt):
        if self.file_dlg.ShowModal() == wx.ID_OK:
            fname = self.file_dlg.GetFilename()
            fdir = self.file_dlg.GetDirectory()
            self.text.LoadFile(os.path.join(fdir, fname) )
    def SetHandlers(self, frame):
        BasePatternMatchingPane.SetHandlers(self, frame)
        frame.Bind(wx.EVT_BUTTON, self.FileOpen, self.load_file_button)
    def _GetOptionsSizer(self):
        sizer = BasePatternMatchingPane._GetOptionsSizer(self)
        sizer.Add(self.load_file_button, 0, 0, 0)
        return sizer

class SearchReplacePane(BaseSearchReplacePane):
    def __init__(self, *args, **kw):
        BaseSearchReplacePane.__init__(self, *args, **kw)
        self.file_dlg = wx.FileDialog(self, "Choose File", )
        self.load_file_button = wx.Button(self, -1, "load text from file")
    def FileOpen(self, evt):
        if self.file_dlg.ShowModal() == wx.ID_OK:
            fname = self.file_dlg.GetFilename()
            fdir = self.file_dlg.GetDirectory()
            self.text.LoadFile(os.path.join(fdir, fname) )
    def SetHandlers(self, frame):
        BaseSearchReplacePane.SetHandlers(self, frame)
        frame.Bind(wx.EVT_BUTTON, self.FileOpen, self.load_file_button)
    def _GetOptionsSizer(self):
        sizer = BaseSearchReplacePane._GetOptionsSizer(self)
        sizer.Add(self.load_file_button, 0, 0, 0)
        return sizer

class PatternMatchingProblemsPane(BasePatternMatchingPane):
    def __init__(self, *args, **kw):
        BasePatternMatchingPane.__init__(self, *args, **kw)
        self._problem_number = 0
    def _GetTopSizer(self):
        # Layout for description, prev, next, etc.
        pass
    def NextProblem(self, evt):
        pass
    def PrevProblem(self, evt):
        pass
    def LoadProblem(self, number):
        pass


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE

        wx.Frame.__init__(self, *args, **kwds)
        regex_app.style_init()

        self.SetTitle("Regular Expressions")

        self.notebook = wx.Notebook(self)

        self.pm_pane = PatternMatchingPane(self.notebook, -1)
        self.pm_pane.SetHandlers(self)
        self.pm_pane.SetSizer(self.pm_pane.GetSizer())

        self.sr_pane = SearchReplacePane(self.notebook, -1)
        self.sr_pane.SetHandlers(self)
        self.sr_pane.SetSizer(self.sr_pane.GetSizer())

        self.notebook.AddPage(self.pm_pane, "Pattern Matching")
        self.notebook.AddPage(self.sr_pane, "Search and Replace")

        main_sizer = wx.BoxSizer()
        main_sizer.Add(self.notebook, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Layout()

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    main_frame = MainFrame(None, -1, "")
    app.SetTopWindow(main_frame)
    main_frame.Show()
    app.MainLoop()
