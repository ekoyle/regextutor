#!/usr/bin/env python3

import wx
from wx import stc
import regex_app

import os

import problems

pm_problem_filename = "pm.dat"
sr_problem_filename = "sr.dat"


class BasePane(object):
    def _GetOptionsSizer(self):
        my_sizer = wx.BoxSizer(wx.HORIZONTAL)
        my_sizer.Add(wx.StaticText(self, -1, "(Flags)  "), 0, 0, 0)
        self.pattern_flags.AddToSizer(my_sizer)
        return my_sizer


class BasePatternMatchingPane(BasePane):
    pattern = None
    text = None
    pattern_flags = None

    def __init__(self, *args, **kw):
        self.text = regex_app.MyRegexMatchCtrl(self, -1)
        self.pattern_flags = regex_app.RECheckboxes(self)
        self.pattern = regex_app.MyPatternStyledTextCtrl(self, -1)
        self.pattern.AddHandler(self.text.SetRegex)

    def UpdateREFlags(self, evt):
        self.text.SetRegex(flags=self.pattern_flags.GetFlags())

    def SetHandlers(self, frame):
        frame.Bind(stc.EVT_STC_STYLENEEDED, self.text.OnUpdate, self.text)
        frame.Bind(wx.EVT_TEXT, self.pattern.OnUpdate, self.pattern)
        frame.Bind(wx.EVT_CHAR, self.pattern.OnUpdate, self.pattern)
        self.pattern_flags.Bind(self, self.UpdateREFlags)

    def _GetPatternSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Search Pattern"), 0, 0, 0)
        my_sizer.Add(self.pattern, 1, wx.EXPAND, 0)
        return my_sizer

    def _GetOptionsSizer(self):
        my_sizer = wx.BoxSizer(wx.HORIZONTAL)
        my_sizer.Add(wx.StaticText(self, -1, "(Flags)  "), 0, 0, 0)
        self.pattern_flags.AddToSizer(my_sizer)
        return my_sizer

    def _GetTextSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Matched Text"), 0, 0, 0)
        my_sizer.Add(self.text, 1, wx.EXPAND, 0)
        return my_sizer

    def _GetTopSizer(self):
        return None

    def GetSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        x = self._GetTopSizer()
        if x:
            my_sizer.Add(x, 1, wx.EXPAND, 0)
        my_sizer.Add(self._GetPatternSizer(), 1, wx.EXPAND, 0)
        my_sizer.Add(self._GetOptionsSizer(), 0, wx.EXPAND, 0)
        my_sizer.Add(self._GetTextSizer(), 4, wx.EXPAND, 0)
        return my_sizer


class BaseSearchReplacePane(BasePane):
    def __init__(self, *args, **kw):
        self.replace_pattern = regex_app.MyReplacePatternStyledTextCtrl(self, -1, "")
        self.replace_text = regex_app.MyReplaceTextCtrl(self, -1)
        self.pattern.AddHandler(self.replace_text.SetRegex)
        self.replace_pattern.AddHandler(self.replace_text.SetValues)
        self.text.AddHandler(self.replace_text.SetValues)

    def SetHandlers(self, frame):
        frame.Bind(wx.EVT_TEXT, self.replace_pattern.OnUpdate, self.replace_pattern)
        frame.Bind(wx.EVT_CHAR, self.replace_pattern.OnUpdate, self.replace_pattern)

    # FIXME: is this needed?
    # def UpdateREFlags(self, evt):
    #    BasePatternMatchingPane.UpdateREFlags(self, evt)
    #    self.replace_text.SetRegex( flags=self.pattern_flags.GetFlags() )
    def _GetReplacePatternSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Replace with"), 0, 0, 0)
        my_sizer.Add(self.replace_pattern, 1, wx.EXPAND, 0)
        return my_sizer

    def _GetReplaceTextSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Replaced Text"), 0, 0, 0)
        my_sizer.Add(self.replace_text, 4, wx.EXPAND, 0)
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
        my_sizer.Add(text, 4, wx.EXPAND, 0)
        return my_sizer


class PatternMatchingPane(BasePatternMatchingPane, wx.Panel):
    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        BasePatternMatchingPane.__init__(self, *args, **kw)
        self.file_dlg = wx.FileDialog(self, "Choose File",)
        self.load_file_button = wx.Button(
            self, -1, "load text from file", style=wx.BU_EXACTFIT
        )

    def FileOpen(self, evt):
        if self.file_dlg.ShowModal() == wx.ID_OK:
            fname = self.file_dlg.GetFilename()
            fdir = self.file_dlg.GetDirectory()
            self.text.LoadFile(os.path.join(fdir, fname))

    def SetHandlers(self, frame):
        BasePatternMatchingPane.SetHandlers(self, frame)
        frame.Bind(wx.EVT_BUTTON, self.FileOpen, self.load_file_button)

    def _GetOptionsSizer(self):
        sizer = BasePatternMatchingPane._GetOptionsSizer(self)
        sizer.Add(self.load_file_button, 0, 0, 0)
        return sizer


class SearchReplacePane(BaseSearchReplacePane, BasePatternMatchingPane, wx.Panel):
    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        BasePatternMatchingPane.__init__(self, *args, **kw)
        BaseSearchReplacePane.__init__(self, *args, **kw)
        self.file_dlg = wx.FileDialog(self, "Choose File",)
        self.load_file_button = wx.Button(
            self, -1, "load text from file", style=wx.BU_EXACTFIT
        )

    def FileOpen(self, evt):
        if self.file_dlg.ShowModal() == wx.ID_OK:
            fname = self.file_dlg.GetFilename()
            fdir = self.file_dlg.GetDirectory()
            self.text.LoadFile(os.path.join(fdir, fname))

    def SetHandlers(self, frame):
        BaseSearchReplacePane.SetHandlers(self, frame)
        BasePatternMatchingPane.SetHandlers(self, frame)
        frame.Bind(wx.EVT_BUTTON, self.FileOpen, self.load_file_button)

    def _GetOptionsSizer(self):
        sizer = BaseSearchReplacePane._GetOptionsSizer(self)
        sizer.Add(self.load_file_button, 0, 0, 0)
        return sizer


class BasePatternMatchingProblemsPane(BasePatternMatchingPane):
    def __init__(self, *args, **kw):
        BasePatternMatchingPane.__init__(self, *args, **kw)
        self.correcting_button = wx.ToggleButton(
            self, -1, "Check Solution", style=wx.BU_EXACTFIT
        )
        self.hint_button = wx.Button(self, -1, "Show Hint", style=wx.BU_EXACTFIT)
        self.back = wx.Button(self, -1, "< Previous", style=wx.BU_EXACTFIT)
        self.forward = wx.Button(self, -1, "Next >", style=wx.BU_EXACTFIT)
        self.problem_description = regex_app.MyROTextCtrl(self)
        self._problem_number = 0
        self._load_problems()
        self.back.Disable()

    def _load_problems(self):
        self._problems = problems.LoadPMProblems()

    def _GetNavSizer(self):
        my_sizer = wx.BoxSizer(wx.HORIZONTAL)
        my_sizer.Add(self.correcting_button, 0, 0, 0)
        my_sizer.Add(self.hint_button, 0, 0, 0)
        my_sizer.Add(self.back, 0, 0, 0)
        my_sizer.Add(self.forward, 0, 0, 0)
        # my_sizer.Add(self., 0, 0, 0)
        return my_sizer

    def _GetProblemSizer(self):
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(wx.StaticText(self, -1, "Problem"), 0, 0, 0)
        my_sizer.Add(self.problem_description, 1, wx.EXPAND, 0)
        return my_sizer

    def _GetTopSizer(self):
        # Layout for description, prev, next, etc.
        my_sizer = wx.BoxSizer(wx.VERTICAL)
        my_sizer.Add(self._GetProblemSizer(), 1, wx.EXPAND, 0)
        my_sizer.Add(self._GetNavSizer(), 0, wx.EXPAND, 0)
        return my_sizer

    def SetHandlers(self, frame):
        BasePatternMatchingPane.SetHandlers(self, frame)
        frame.Bind(wx.EVT_TOGGLEBUTTON, self.ToggleCorrecting, self.correcting_button)
        frame.Bind(wx.EVT_BUTTON, self.ShowHint, self.hint_button)
        frame.Bind(wx.EVT_BUTTON, self.NextProblem, self.forward)
        frame.Bind(wx.EVT_BUTTON, self.PrevProblem, self.back)

    def ToggleCorrecting(self, evt):
        correcting = self.correcting_button.GetValue()
        self.text.SetShowCorrections(correcting)

    def ShowHint(self, evt):
        problem = self._problems[self._problem_number]
        dlg = wx.MessageDialog(self, message=problem.hint, caption="Hint", style=wx.OK)
        dlg.ShowModal()
        del dlg

    def NextProblem(self, evt):
        print("NextProblem")
        curr = self._problem_number
        n = curr + 1
        if n < len(self._problems):
            self.LoadProblem(n)
            if curr == 0:
                self.back.Enable()
            if n == (len(self._problems) - 1):
                self.forward.Disable()

    def PrevProblem(self, evt):
        print("PrevProblem")
        curr = self._problem_number
        p = curr - 1
        if p >= 0:
            self.LoadProblem(p)
            if p == 0:
                self.back.Disable()
            if curr == (len(self._problems) - 1):
                self.forward.Enable()

    def LoadProblem(self, number=None):
        print("LoadProblem(%s)" % number)
        if number is None:
            number = self._problem_number
        oldproblem = self._problems[self._problem_number]
        oldproblem.user_pattern = self.pattern.GetValue()
        problem = self._problems[number]
        self._LoadProblem(oldproblem, problem)
        self.problem_description.SetText(
            "Problem %d: %s" % (number + 1, problem.description)
        )
        if oldproblem.user_pattern != problem.user_pattern:
            # It gets unhappy if you set it to its current value :/
            self.pattern.SetValue(problem.user_pattern)
        self.text.SetPreferred(problem.solution_pattern, problem.flags)
        self.text.SetText(problem.test)
        self.correcting_button.SetValue(False)
        self.ToggleCorrecting(None)
        self._problem_number = number
        return oldproblem, problem

    def _LoadProblem(self, oldproblem, newproblem):
        pass


class PatternMatchingProblemsPane(BasePatternMatchingProblemsPane, wx.Panel):
    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        BasePatternMatchingProblemsPane.__init__(self, *args, **kw)


class SearchReplaceProblemsPane(
    BaseSearchReplacePane, BasePatternMatchingProblemsPane, wx.Panel
):
    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
        BasePatternMatchingProblemsPane.__init__(self, *args, **kw)
        BaseSearchReplacePane.__init__(self, *args, **kw)

    def _load_problems(self):
        self._problems = problems.LoadSRProblems()

    def _LoadProblem(self, oldproblem, problem):
        oldproblem.user_replace = self.replace_pattern.GetValue()
        if oldproblem.user_replace != problem.user_replace:
            self.replace_pattern.SetValue(problem.user_replace)

    def SetHandlers(self, frame):
        BaseSearchReplacePane.SetHandlers(self, frame)
        BasePatternMatchingProblemsPane.SetHandlers(self, frame)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE

        wx.Frame.__init__(self, *args, **kwds)
        regex_app.style_init()

        self.SetTitle("Regular Expressions")

        self.notebook = wx.Notebook(self)

        self.pm_problem_pane = PatternMatchingProblemsPane(self.notebook, -1)
        self.pm_problem_pane.LoadProblem()
        self.pm_problem_pane.SetHandlers(self)
        self.pm_problem_pane.SetSizer(self.pm_problem_pane.GetSizer())

        self.pm_pane = PatternMatchingPane(self.notebook, -1)
        self.pm_pane.SetHandlers(self)
        self.pm_pane.SetSizer(self.pm_pane.GetSizer())

        self.sr_problem_pane = SearchReplaceProblemsPane(self.notebook, -1)
        self.sr_problem_pane.LoadProblem()
        self.sr_problem_pane.SetHandlers(self)
        self.sr_problem_pane.SetSizer(self.sr_problem_pane.GetSizer())

        self.sr_pane = SearchReplacePane(self.notebook, -1)
        self.sr_pane.SetHandlers(self)
        self.sr_pane.SetSizer(self.sr_pane.GetSizer())

        self.notebook.AddPage(self.pm_pane, "Pattern Matching")
        self.notebook.AddPage(self.pm_problem_pane, "PM Problems")
        self.notebook.AddPage(self.sr_pane, "Search and Replace")
        self.notebook.AddPage(self.sr_problem_pane, "SR Problems")

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
