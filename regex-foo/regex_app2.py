#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Fri Sep 10 09:05:06 2010

import wx
import re

# begin wxGlade: extracode
from wx import stc
# end wxGlade

STYLE_OVERLAP=0x80 # underline
STYLE_DEFAULT=0x00

style_definitions = {
        0x00:'fore:#ffffff,back:#000000',
        0x01:'fore:#ff5555,back:#000000,bold',
        0x02:'fore:#55ff55,back:#000000,bold',
        0x03:'fore:#5555ff,back:#000000,bold',
        0x04:'fore:#55ffff,back:#000000,bold',
        0x05:'fore:#ff55ff,back:#000000,bold',
        0x06:'fore:#ffff55,back:#000000,bold',
        0x07:'fore:#ff0000,back:#000000,bold',
        0x08:'fore:#00ff00,back:#000000,bold',
        0x09:'fore:#0000ff,back:#000000,bold',
        0x0a:'fore:#00ffff,back:#000000,bold',
        0x0b:'fore:#ff00ff,back:#000000,bold',
        0x0c:'fore:#ffff00,back:#000000,bold',
        0x0d:'fore:#ffaaaa,back:#000000,bold',
        0x0e:'fore:#aaffaa,back:#000000,bold',
        0x0f:'fore:#aaaaff,back:#000000,bold',
        0x11:'fore:#ff5555,back:#550000,bold',
        0x12:'fore:#55ff55,back:#550000,bold',
        0x13:'fore:#5555ff,back:#550000,bold',
        0x14:'fore:#55ffff,back:#550000,bold',
        0x15:'fore:#ff55ff,back:#550000,bold',
        0x16:'fore:#ffff55,back:#550000,bold',
        0x17:'fore:#ff0000,back:#550000,bold',
        0x18:'fore:#00ff00,back:#550000,bold',
        0x19:'fore:#0000ff,back:#550000,bold',
        0x1a:'fore:#00ffff,back:#550000,bold',
        0x1b:'fore:#ff00ff,back:#550000,bold',
        0x1c:'fore:#ffff00,back:#550000,bold',
        0x1d:'fore:#ffaaaa,back:#550000,bold',
        0x1e:'fore:#aaffaa,back:#550000,bold',
        0x1f:'fore:#aaaaff,back:#550000,bold',
        0x20:'fore:#ffffff,back:#0000000' # "default"
        }

class MyPatternStyledTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kw):
        wx.TextCtrl.__init__(self, *args, **kw)
        self._re_style='Extended'
    def SetTextBox(self, box):
        self.__text_box = box
    def SetReStyle(self, style):
        self._re_style = style
        self.OnUpdate(None)
    def ConvertRegex(self, regex):
        if self._re_style == 'Extended':
            return regex
        # FIXME: replace \( with (, ( with \(, but not inside []...
    def OnUpdate(self, evt):
        print 'OnUpdate'
        regex = self.GetValue()
        regex = self.ConvertRegex(regex)
        print regex
        if '\n' in regex:
            # oops
            pass
        # pretty colors, please
        # update text box
        self.__text_box.SetRegex(regex)
    
class MyReChoice(wx.Choice):
    def SetTextCtrl(self, ctrl):
        self._text_ctrl = ctrl
    def OnChange(self, evt):
        self._text_ctrl.SetReStyle(self.GetSelection)

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.notebook_1 = wx.Notebook(self)
        self.pattern_matching_pane = wx.Panel(self.notebook_1, -1)
        self.search_replace_pane = wx.Panel(self.notebook_1, -1)

        self.pattern_match_pattern = MyPatternStyledTextCtrl(self.pattern_matching_pane, -1)
        self.load_file_button = wx.Button(self.pattern_matching_pane, -1, "load text from file")
        self.regex_type_choice = MyReChoice(self.pattern_matching_pane, -1, choices=["Extended", "POSIX", ])
        self.pattern_match_text = MyStyledTextCtrl(self.pattern_matching_pane, -1)

        self.search_pattern = MyPatternStyledTextCtrl(self.search_replace_pane, -1, "")
        self.search_text_box = MyStyledTextCtrl(self.search_replace_pane, -1)
        self.replace_pattern = MyPatternStyledTextCtrl(self.search_replace_pane, -1, "")
        self.replace_text_box = MyStyledTextCtrl(self.search_replace_pane, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        #self.pattern_match_text.pattern = self.search_pattern
        self.pattern_match_text.SetLexer(stc.STC_LEX_CONTAINER)
        self.Bind(stc.EVT_STC_STYLENEEDED, self.pattern_match_text.DoRegexStyle, self.pattern_match_text)
        self.Bind(wx.EVT_TEXT, self.pattern_match_pattern.OnUpdate, self.pattern_match_pattern)
        self.Bind(wx.EVT_CHAR, self.pattern_match_pattern.OnUpdate, self.pattern_match_pattern)
        for k in sorted(style_definitions.keys()):
            self.pattern_match_text.StyleSetSpec(k, style_definitions[k])
            #print "k: 0x%02x, style: %s" % (k,style_definitions[k])
        #self.__test_styles(self.pattern_match_text)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("frame_1")
        self.regex_type_choice.SetSelection(0)
        # end wxGlade
        self.pattern_match_pattern.SetTextBox(self.pattern_match_text)

    def __do_layout(self):
        #main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer()
        
        pattern_options_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pattern_options_sizer.Add(self.load_file_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        pattern_options_sizer.Add(self.regex_type_choice, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)

        main_pattern_sizer = wx.BoxSizer(wx.VERTICAL)
        main_pattern_sizer.Add(self.pattern_match_pattern, 0, wx.EXPAND, 0)
        main_pattern_sizer.Add(pattern_options_sizer, 0, wx.EXPAND, 0)
        main_pattern_sizer.Add(self.pattern_match_text, 3, wx.EXPAND, 0)
        self.pattern_matching_pane.SetSizer(main_pattern_sizer)

        
        search_sizer = wx.BoxSizer(wx.VERTICAL)
        search_sizer.Add(self.search_pattern, 0, wx.EXPAND, 0)
        search_sizer.Add(self.search_text_box, 3, wx.EXPAND, 0)

        replace_sizer = wx.BoxSizer(wx.VERTICAL)
        replace_sizer.Add(self.replace_pattern, 0, wx.EXPAND, 0)
        replace_sizer.Add(self.replace_text_box, 3, wx.EXPAND, 0)

        main_sr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sr_sizer.Add(search_sizer, 1, wx.EXPAND, 0)
        main_sr_sizer.Add(replace_sizer, 1, wx.EXPAND, 0)

        self.search_replace_pane.SetSizer(main_sr_sizer)
        
        self.notebook_1.AddPage(self.pattern_matching_pane, "Pattern Matching")
        self.notebook_1.AddPage(self.search_replace_pane, "Search and Replace")

        main_sizer.Add(self.notebook_1, 1, wx.EXPAND, 0)
        
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Layout()

    def __test_styles(self, ctrl):
        ctrl.ClearAll()
        lines = []
        for i in range(32):
            line = '0x%x - %s - ABCabc123\n' % (i,style_definitions[i])
            style =  chr(i)
            #line2 = '0x%x - %s - ? - ABCabc123\n' % ((i << 3), style_definitions[i])
            #style2 = chr(i<<3)
            lines.append(style.join(line))
            lines.append('\x00')
            #lines.append(style2.join(line2))
            #lines.append('\x00')
        ctrl.AddStyledText(''.join(lines))
            
    
#    def DoPatternStyle(self, evt):
#        self.DoRegexStyle( evt, self.pattern_match_text, self.pattern_match_pattern)
    
class MyStyledTextCtrl(stc.StyledTextCtrl):
    def SetRegex(self, regex):
        self._regex = re.compile(regex)
        print "SetRegex(%s)" % regex
        print self
        self.DoRegexStyle(None)
    def get_style(self, group_num):
        return (group_num % 32) + 1
    def DoRegexStyle(self, evt):
        if not hasattr(self,'_regex'):
            print '_regex undefined'
            return
        print 'DoRegexStyle'
        #print dir(evt)
        #self.GetEndStyled()
        #regex = re.compile(r'abc(.)(.)(.(.).)')
        #print evt.Position
        current = self.GetFirstVisibleLine()
        while(self.GetLineVisible(current)):
            line_start = self.PositionFromLine(current)
            if line_start < 0:
                break
            line = self.GetLine(current)

            print line, line_start
            match = self._regex.search(line)
            style = [STYLE_DEFAULT] * len(line)
            if match:
                num_groups = len(match.groups())
                for i in range(num_groups+1):
                    for j in range(match.start(i), match.end(i)):
                        new_style = self.get_style(i)
                        if style[j] != STYLE_DEFAULT:
                            style[j] = new_style | STYLE_OVERLAP
                        else:
                            style[j] = new_style
            self.StartStyling(line_start,0xff)
            print 'StartStyling(%s,...)' % line_start
            style_str = ''.join(map(chr,style))
            self.SetStyleBytes(len(style), style_str)
            print 'SetStyleBytes(...,%s)' % style
            current += 1


# end of class MyFrame


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
