#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6.3 on Fri Sep 10 09:05:06 2010

import wx
import re
import re_parse
import os

import time

import thread

# begin wxGlade: extracode
from wx import stc
# end wxGlade

STYLE_OVERLAP=0x80 # underline
STYLE_DEFAULT=0x0

group_color_names = [
        'WHITE', # N/A
        'CYAN',
        'GREEN',
        'YELLOW',
        'ORANGE',
        'ORANGE RED',
        'VIOLET',
        'VIOLET RED',

        # Valid colors are: 'AQUAMARINE', 'BLACK', 'BLUE', 'BLUE VIOLET', 'BROWN', 'CADET BLUE', 'CORAL', 'CORNFLOWER BLUE', 'CYAN', 'DARK GREY', 'DARK GREEN', 'DARK OLIVE GREEN', 'DARK ORCHID', 'DARK SLATE BLUE', 'DARK SLATE GREY', 'DARK TURQUOISE', 'DIM GREY', 'FIREBRICK', 'FOREST GREEN', 'GOLD', 'GOLDENROD', 'GREY', 'GREEN', 'GREEN YELLOW', 'INDIAN RED', 'KHAKI', 'LIGHT BLUE', 'LIGHT GREY', 'LIGHT STEEL BLUE', 'LIME GREEN', 'MAGENTA', 'MAROON', 'MEDIUM AQUAMARINE', 'MEDIUM BLUE', 'MEDIUM FOREST GREEN', 'MEDIUM GOLDENROD', 'MEDIUM ORCHID', 'MEDIUM SEA GREEN', 'MEDIUM SLATE BLUE', 'MEDIUM SPRING GREEN', 'MEDIUM TURQUOISE', 'MEDIUM VIOLET RED', 'MIDNIGHT BLUE', 'NAVY', 'ORANGE', 'ORANGE RED', 'ORCHID', 'PALE GREEN', 'PINK', 'PLUM', 'PURPLE', 'RED', 'SALMON', 'SEA GREEN', 'SIENNA', 'SKY BLUE', 'SLATE BLUE', 'SPRING GREEN', 'STEEL BLUE', 'TAN', 'THISTLE', 'TURQUOISE', 'VIOLET', 'VIOLET RED', 'WHEAT', 'WHITE', 'YELLOW', 'YELLOW GREEN',
        ]

group_styles = None
default_font = None
default_style = None
DUPL_STYLE = None
BRACKET_STYLE = None
STR_ESC_STYLE = None
RE_ESC_STYLE = None
RANGE_STYLE = None
INVALID_STYLE = None

FONT_SIZE=14

STYLE_MASK = stc.STC_INDICS_MASK
STYLE_UNDERLINE=stc.STC_INDIC1_MASK
STYLE_STRIKETHROUGH = stc.STC_INDIC2_MASK

STYLE_UNDERLINE_NO = 1
STYLE_STRIKETHROUGH_NO = 2

log_level = 1
#log_level = 1|2|4|8
timing = 1
timing_threshold = 0.1

def log(level, fcn, s, sub=None,):
    try:
        if level & log_level:
            if sub:
                s = s % sub
            print fcn+': ', s
    except Exception, e:
        print e
        print level, fcn, s, sub

class MyTextStyle(object):
    # this will be slow, but I don't really mind much
    def __init__(self):
        # list of (start, stop, style)
        self.__data = []
    def set_style(self, start, stop, style):
        d_match = None
        log(8, "MyTextStyle.set_style", "start: %s, stop: %s", (start, stop))
        print_style(style)
        # Try to find the most-specific current style
        for i in range(len(self.__data)):
            d = self.__data[i]
            d_start, d_stop, d_style = d
            log(8, "MyTextStyle.set_style", "d_start: %s, d_stop: %s", (d_start, d_stop) )
            if start >= d_start and start <= d_stop:
                print d_start, start, stop, d_stop
                # sub-range?
                if d_stop < stop:
                    e = Exception('attempted to style across style boundaries -- bad')
                    print e
                    raise e
                d_match = i
                break
        if d_match is not None:
            log(8, "MyTextStyle.set_style", "d_match: %s" % d_match)
            self.__data.insert( d_match, (start, stop, style) )
        else:
            log(8, "MyTextStyle.set_style", "!d_match")
            self.__data.append( (start, stop, style) )
    def get_style(self, pos):
        for i in range(len(self.__data)):
             d_start, d_stop, d_style = self.__data[i]
             if pos >= d_start and pos < d_stop:
                 return d_style
        return default_style
    def get_style_data(self):
        return sorted(self.__data[:])

def style_init():
    # wx is goofy about fonts... we have to create an App first...
    global DUPL_STYLE
    DUPL_STYLE = wx.TextAttr(wx.NullColour,"NAVY")
    bracket_font = wx.Font(FONT_SIZE,wx.FONTSTYLE_NORMAL,wx.NORMAL,wx.FONTWEIGHT_BOLD,faceName='Courier')
    global BRACKET_STYLE
    #BRACKET_STYLE = wx.TextAttr(wx.NullColour,"DARK GREY",bracket_font)
    BRACKET_STYLE = wx.TextAttr(wx.NullColour,wx.NullColour,bracket_font)
    global group_styles
    group_styles = [ wx.TextAttr( i, wx.NullColour ) for i in group_color_names ]
    global default_font
    default_font = wx.Font(12,wx.FONTSTYLE_NORMAL,wx.NORMAL,wx.FONTWEIGHT_NORMAL,faceName='Courier')
    global default_style
    default_style = wx.TextAttr( 'WHITE', 'BLACK', default_font)
    global STR_ESC_STYLE
    STR_ESC_STYLE = wx.TextAttr( 'LIGHT GREEN', wx.NullColour)
    global RE_ESC_STYLE
    RE_ESC_STYLE = wx.TextAttr( 'LIGHT BLUE', wx.NullColour )
    global RANGE_STYLE
    RANGE_STYLE = wx.TextAttr(wx.NullColour, wx.NullColour, default_font)
    global INVALID_STYLE
    INVALID_STYLE = wx.TextAttr('LIGHT BLUE', 'DARK RED', default_font)

def print_style(style):
    try:
        log( 8, 'print_style', 'Font: %s Color: %s BG Color: %s', (style.GetFont(), style.GetTextColour(), style.GetBackgroundColour()) )
    except Exception, e:
        print e
        raise

class MyROTextCtrl(stc.StyledTextCtrl):
    def __init__(self, *args, **kw):
        stc.StyledTextCtrl.__init__(self, *args, **kw)
        self.StyleSetSpec( 0x20, 'fore:#ffffff,back:#0000000,face:Courier,size:%s' % FONT_SIZE) # "default"
        self.StyleSetSpec( 0x00, 'fore:#ffffff,back:#0000000,face:Courier,size:%s' % FONT_SIZE)
        #self.SetReadOnly(True)
        self.SetWrapMode(stc.STC_WRAP_WORD) # wrap, please
        self.SetText("Forgot to initialize text...")
        self.SetScrollWidth(400)
        self.SetHighlightGuide(0)
        self.SetMarginWidth(1,0)
    def SetText(self, text):
        self.SetReadOnly(False)
        stc.StyledTextCtrl.SetText(self, text)
        self.SetReadOnly(True)

class MyPatternStyledTextCtrl(wx.TextCtrl):
    def __init__(self, *args, **kw):
        if not kw.has_key('style'):
            kw['style'] = wx.TE_RICH2 | wx.TE_MULTILINE
        wx.TextCtrl.__init__(self, *args, **kw)
        if not self.SetDefaultStyle( default_style ):
            log(1, 'MyPatternStyledTextCtrl.__init__', "Failed to set default style")
        self.SetBackgroundColour('BLACK')
        self.SetForegroundColour('WHITE')
        self.SetFont(default_font)
        self._re_style='Extended'
        if self._re_style == 'Extended':
            self._re_parser = re_parse.ExtendedREParser(self)
        self.__callbacks = []
        self._text = ''
        self.__on_update = False
    def AddHandler(self, handler):
        self.__callbacks.append(handler)
    def SetReStyle(self, style):
        self._re_style = style
        self.OnUpdate(caller='MyPatternStyledTextCtrl.SetReStyle')
    def ConvertRegex(self, regex):
        if self._re_style == 'Extended':
            return regex
        # FIXME: replace \( with (, ( with \(, but not inside []...
    def _CallHandlers(self, *args, **kw):
        for callback in self.__callbacks:
            try:
                callback(*args, **kw)
            except Exception,e:
                log(1, 'MyPatternStyledTextCtrl._CallHandlers', e)
                raise
    def OnUpdate(self, evt=None, **kw):
        if timing:
            __start_time = time.time()
        if self.__on_update:
            return # hopefully that wasn't the last one...
        self.__on_update = True
        log(4, 'MyPatternStyledTextCtrl.OnUpdate', '(%s,%s)', (evt, kw))
        if evt:
            log(16, 'MyPatternStyledTextCtrl.OnUpdate', (evt.IsCommandEvent(),evt.GetEventType(),))

        text = self.GetValue()
        if self._text == text:
            return # nothing changed
        self._text = text
        # do some color foo
        try:
            ign = self._re_parser.parse(self._text)
        except:
            pass
        regex = self.ConvertRegex(self._text)
        if '\n' in regex:
            # oops
            pass
        # pretty colors, please
        # update text box
        self._CallHandlers(regex=regex, regex_text=self._text)
        if timing:
            __stop_time = time.time()
            __time_delta = __stop_time-__start_time
            if __time_delta > timing_threshold:
                print 'MyPatternStyledTextCtrl.OnUpdate: ',__stop_time-__start_time
        self.__on_update = False
    def startParsing(self,s):
        self._clear_style()
        self.parse_groups = {}
        self.parse_string = s
        self.parse_format = [0] * len(s)
        self.parse_operations = []
        self.num_groups = None
    def endParsing(self):
        self.__curr_group = 1
        self.num_groups = len(self.parse_groups)
        for k in sorted(self.parse_groups.keys()):
            self.colorGroup( *(self.parse_groups[k]) )
            self.__curr_group += 1
        for operation, args in self.parse_operations:
            operation(*args)
        self._apply_style()
        del self.__curr_group
    def handleType(self, s, loc, toks, t_func):
        self.parse_operations.insert(0, (t_func, (loc, re_parse.toklen(toks[0]),
            loc+re_parse.toklen(toks) - re_parse.toklen(toks[-1]), re_parse.toklen(toks[-1]))) )
    def handleDupl(self, s, loc, toks):
        self.handleType(s,loc,toks,self.colorDupl)
    def handleGroup(self, s, loc, toks):
        #self.handleType(s,loc,toks,self.colorGroup)
        self.parse_groups[loc] = (loc, re_parse.toklen(toks[0]),
                loc+re_parse.toklen(toks) - re_parse.toklen(toks[-1]), re_parse.toklen(toks[-1]), )
    def handleBracketList(self, s, loc, toks):
        self.handleType(s,loc,toks,self.colorBracketList)
    def handleReEscape(self, s, loc, toks):
        self.handleType(s,loc,toks,self.colorReEscape)
    def handleStringEscape(self, s, loc, toks):
        self.handleType(s,loc,toks,self.colorStringEscape)
    def handleRange(self, s, loc, toks):
        self.handleType(s,loc,toks,self.colorRange)
    def handleBackreference(self, s, loc, toks):
        self.handleType(s,loc,toks,self.colorBackreference)
    def handleInvalid(self, s, loc, toks):
        self.handleType(s, loc, toks, self.colorInvalid)
    def setTextStyle_direct(self, start, end, style):
        ins_point = self.GetInsertionPoint()
        curr_style = wx.TextAttr()
        self.SetInsertionPoint(0)
        if not self.SetStyle( start, end, curr_style.Merge(style, curr_style) ): log(1, 'MyPatternStyledTextCtrl.setTextStyle_direct', 'Failed to set color')
        self.SetInsertionPoint(ins_point)
    def _clear_style(self):
        self._style = MyTextStyle()
    def _apply_style(self):
        ins_point = self.GetInsertionPoint()
        self.SetInsertionPoint(0)
        self.SetStyle(0,len(self._text), default_style)
        for start, end, style in self._style.get_style_data():
            self.SetInsertionPoint(0)
            if not self.SetStyle( start, end, style ): log(1, 'MyPatternStyledTextCtrl.setTextStyle', 'Failed to set style: (%s,%s,%s)', (start,end,style))
        self.SetInsertionPoint(ins_point)
    def setTextStyle(self, start, end, style):
        curr_style = self._style.get_style(start)
        use_style = curr_style.Merge(curr_style, style)
        self._style.set_style(start, end, use_style)
    def colorDupl(self, start, startlen, end, endlen):
        self.setTextStyle( start, end + endlen, DUPL_STYLE )
    def colorGroup(self, start, startlen, end, endlen):
        group_num = self.__curr_group
        self.setTextStyle( start, end + endlen, group_styles[group_num] )
    def colorBracketList(self, start, startlen, end, endlen):
        self.setTextStyle( start, end + endlen, BRACKET_STYLE )
    def colorReEscape(self, start, startlen, end, endlen):
        self.setTextStyle( start, end + endlen, RE_ESC_STYLE )
    def colorStringEscape(self, start, startlen, end, endlen):
        self.setTextStyle( start, end + endlen, STR_ESC_STYLE )
    def colorRange(self, start, startlen, end, endlen):
        self.setTextStyle( start, end + endlen, RANGE_STYLE )
    def colorBackreference(self, start, startlen, end, endlen):
        group_num = int(self.parse_string[start+1:end+endlen])
        self.setTextStyle( start, end + endlen, group_styles[group_num] )
    def colorInvalid(self, start, startlen, end, endlen):
        self.setTextStyle( start, end+endlen, INVALID_STYLE )


class MyReplacePatternStyledTextCtrl(MyPatternStyledTextCtrl):
    def __init__(self, *args, **kw):
        MyPatternStyledTextCtrl.__init__(self, *args, **kw)
        self._pattern_parser = re_parse.ReplacePatternParser(self)
        self.__on_update = False
    def OnUpdate(self, evt=None, **kw):
        if timing:
            __start_time = time.time()
        if self.__on_update:
            raise Exception("OnUpdate called from OnUpdate?!")
        self.__on_update = True
        try:
            log(4, "MyReplacePatternStyledTextCtrl", "(%s, %s)", (evt, kw) )
            wx.Yield()
            newtext = self.GetValue()
            if newtext != self._text:
                self._text = newtext
                ign = self._pattern_parser.parse(self._text)
                self._CallHandlers(replace=self._text)
            if timing:
                __stop_time = time.time()
                __time_delta = __stop_time-__start_time
                if __time_delta > timing_threshold:
                    print 'MyPatternStyledTextCtrl.OnUpdate: ',__stop_time-__start_time
        finally:
            self.__on_update = False

RE_MATCH_MARKER = 1
RE_TOOMUCH_MARKER = 2
RE_MISSED_MARKER = 3

class MyStyledTextCtrl(wx.stc.StyledTextCtrl):
    def __init__(self, *args, **kw):
        stc.StyledTextCtrl.__init__(self, *args, **kw)
        self.StyleSetSpec( 0x20, 'fore:#808080,back:#0000000,face:Courier,size:%s' % FONT_SIZE) # "default"
        self.StyleSetSpec( 0x00, 'fore:#808080,back:#0000000,face:Courier,size:%s' % FONT_SIZE)
        self.SetLexer(stc.STC_LEX_CONTAINER)
        self.SetScrollWidth(800)
        self._callbacks = []
        self._text = ''
        for i in range(len(group_color_names)):
            self.StyleSetForeground(i+1,group_color_names[i])
            self.StyleSetBackground(i+1,'BLACK')
        self._regex_text = ''
        self._regex_flags = re.MULTILINE
        self._regex=re.compile(self._regex_text, self._regex_flags)
        self.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(0,30)
        self.SetMarginType(1, stc.STC_MARGIN_SYMBOL)
        self.MarkerDefine(RE_MATCH_MARKER, stc.STC_MARK_ARROW, "GREEN", "BLACK")
        self.MarkerDefine(RE_TOOMUCH_MARKER, stc.STC_MARK_CIRCLEPLUS, "RED", "BLUE")
        self.MarkerDefine(RE_MISSED_MARKER, stc.STC_MARK_CIRCLEMINUS, "RED", "BLUE")
        self.IndicatorSetStyle(STYLE_STRIKETHROUGH_NO, stc.STC_INDIC_STRIKE)
        self.IndicatorSetForeground(STYLE_STRIKETHROUGH_NO, "RED")
        self.IndicatorSetStyle(STYLE_UNDERLINE_NO, stc.STC_INDIC_PLAIN)
        self.IndicatorSetForeground(STYLE_UNDERLINE_NO, "RED")
        self._lock = thread.allocate_lock()
        self._busy_lock = thread.allocate_lock()
    def AddHandler(self, handler):
        self._callbacks.append(handler)
    def _CallHandlers(self, *args, **kw):
        for handler in self._callbacks:
            handler( *args, **kw )
    def SetRegex(self, **kw):
        log(4, "MyStyledTextCtrl.SetRegex", kw)
        recompile = False
        if kw.has_key('flags'):
            flags = kw['flags']
            if self._regex_flags != flags:
                self._regex_flags = flags
                recompile=True
        if kw.has_key('regex_text'):
            regex_text = kw['regex_text']
        else:
            regex_text = self._regex_text
        if recompile or self._regex_text != regex_text:
            self._regex_text = regex_text
            try:
                self._regex = re.compile(self._regex_text, self._regex_flags)
            except:
                log(1, "MyPatternStyledTextCtrl.SetRegex", "Invalid RE: %s" % self._regex)
                self._regex = re.compile("\b\B")
            self._CallHandlers( regex=self._regex, regex_text = self._regex_text )
            self.OnUpdate(caller='MyStyledTextCtrl.SetRegex')
    def OnUpdate(self, evt=None, **kw):
        thread.start_new_thread(self.OnUpdateCommon,(evt,),kw)
    def OnUpdateCommon(self, evt=None, **kw):
        if timing:
            __start_time = time.time()
        if not self._lock.acquire(0):
             if not self._busy_lock.acquire(0):
                 print "Skipping OnUpdate"
                 return
             self._lock.acquire()
             self._busy_lock.release()
        try:
            wx.Yield()
            self._OnUpdate(evt, **kw)
            if timing:
                __stop_time = time.time()
                __time_delta = __stop_time-__start_time
                if __time_delta > timing_threshold:
                    print 'MyPatternStyledTextCtrl.OnUpdate: ',__stop_time-__start_time
        finally:
            self._lock.release()

class MyRegexMatchCtrl(MyStyledTextCtrl):
    def __init__(self, *args, **kw):
        MyStyledTextCtrl.__init__(self, *args, **kw)
        self.SetCaretForeground('WHITE')
        self._preferred = None
        self._show_corrections = None
        self.__on_update = False
    def SetPreferred(self, regex, flags):
        try:
            self._preferred = re.compile(regex, flags)
        except:
            self._preferred = None
    def SetShowCorrections(self, val):
        self._show_corrections = val
        self.OnUpdate()
    def GetShowCorrections(self):
        return self._show_corrections
    def get_style(self, group_num):
        return (group_num % 32) + 1
    def DoRegexStyle(self, evt, **kw):
        if not (hasattr(self,'_regex') or hasattr(self, '_text')):
            log(1, 'MyRegexMatchCtrl.DoRegexStyle', '_regex undefined')
            return

        line = self._text
        line_start = 0

        #self.StyleClearAll()
        wx.CallAfter(self.MarkerDeleteAll,RE_MATCH_MARKER)
        wx.CallAfter(self.MarkerDeleteAll,RE_TOOMUCH_MARKER)
        wx.CallAfter(self.MarkerDeleteAll,RE_MISSED_MARKER)
        style = [STYLE_DEFAULT] * len(line)
        pmatches = None
        if self._preferred and self._show_corrections:
            #print 'Correcting'
            pmatches = self._preferred.finditer(line)
        def _get_next(match_iter):
            try:
                if not match_iter:
                    raise StopIteration('not really an iterator, you know?')
                pcurr = match_iter.next()
                pstart = pcurr.start()
                pend = pcurr.end()
                #print 'pstart: %s, pend: %s' % (pstart, pend)
            except StopIteration:
                pcurr = None
                pstart = None
                pend = None
                #print 'no more pmatches'
            return (pcurr,pstart,pend)

        def __style(start, stop, new_style, mask=0xe0):
            log(8,'MyRegexMatchCtrl.DoRegexStyle', "__style(%s, %s, %s, %s)", (start, stop, new_style, mask))
            for i in xrange(start, stop):
                style[i] = new_style | style[i] & mask
        def __underline(start, stop):
            __style(start, stop, STYLE_UNDERLINE, 0xff)
            wx.CallAfter(self.MarkerAdd,self.GetLineNum(start), RE_MISSED_MARKER)
            #FIXME: set appropriate marker
        def __strikethrough(start, stop):
            __style(start, stop, STYLE_STRIKETHROUGH, 0xff)
            wx.CallAfter(self.MarkerAdd,self.GetLineNum(start), RE_TOOMUCH_MARKER)
            #FIXME: set appropriate marker

        matched = False
        for match in self._regex.finditer(line):
            if not matched:
                (pcurr, pstart, pend) = _get_next(pmatches)
                matched = True
            mstart = match.start()
            mend = match.end()
            #print 'mstart: %s, mend: %s' % (mstart, mend)
            #print pcurr, pstart, pend
            curr_line_no = self.GetLineNum(match.start())
            if not self._show_corrections:
                #print "self.MarkerAdd(%s, %s)" % (curr_line_no, RE_MATCH_MARKER)
                wx.CallAfter(self.MarkerAdd,curr_line_no, RE_MATCH_MARKER)
            #print '_show_corrections: %s, mstart: %s, mend: %s' % (self._show_corrections, mstart, mend)
            m_handled = False
            while pmatches and pcurr:
                if mstart == pstart and mend == pend:
                    #print "mstart == pstart and mend == pend"
                    # Great job! moving on...
                    m_handled = True
                    (pcurr, pstart, pend) = _get_next(pmatches)
                    break
                elif mstart > pend:
                    #print "mstart > pend"
                    # Missed completely, none of this was matched, but it should have been
                    __underline(pstart, pend)
                elif mend < pstart:
                    #print "mend < pstart"
                    __strikethrough(mstart, mend)
                    m_handled = True
                    break
                else:
                    #print "else"
                    # we have some overlap :(
                    if mstart < pstart:
                        #print "-- mstart < pstart"
                        __strikethrough(mstart, pstart)
                    if pstart < mstart:
                        #print "-- pstart < mstart"
                        __underline(pstart, mstart)
                    if pend < mend:
                        if pstart >= mstart:
                            m_handled = True
                        #print "-- pend < mend"
                        __strikethrough(pend, mend)
                    if mend < pend:
                        #print "--mend < pend"
                        m_handled = True
                        __underline(mend, pend)
                        break
                    elif mend == pend:
                        #print "--mend == pend"
                        m_handled = True
                        (pcurr, pstart, pend) = _get_next(pmatches)
                        break
                    # FIXME: Mark this line accordingly
                (pcurr, pstart, pend) = _get_next(pmatches)
            if self._show_corrections and not pcurr and not m_handled:
                #print "self._show_corrections: %s pcurr: %s m_handled: %s" % (self._show_corrections,pcurr, m_handled)
                __strikethrough(mstart, mend)
            num_groups = len(match.groups())
            for i in range(num_groups+1):
                new_style = self.get_style(i)
                __style(match.start(i), match.end(i), new_style)
        if not matched and pmatches:
            for m in pmatches:
                __underline(m.start(), m.end())
        wx.CallAfter(self.StartStyling, line_start, 0xff)
        style_str = ''.join(map(chr,style))
        wx.CallAfter(self.SetStyleBytes, len(style), style_str)
    def GetLineNum( self, pos ):
        for i in xrange(len(self._text_line_start)):
            if self._text_line_start[i] > pos:
                return i-1
        return len(self._text_line_start)-1
    def _OnUpdate(self, evt=None, **kw):
            log(4, "MyRegexMatchCtrl._OnUpdate", "(%s, %s)", (evt, kw) )
            new_text = self.GetText()
            if new_text is None:
                new_text = ''
            if new_text != self._text:
                self._text = new_text
                self._text_line_start = [0]
                curr = 0
                for i in xrange(len(self._text)):
                    if self._text[i] == '\n':
                        self._text_line_start.append(i+1)
                wx.CallAfter(self._CallHandlers, text=self._text)
            self.DoRegexStyle(None)

class MyReplaceTextCtrl(MyStyledTextCtrl):
    def __init__(self, *args, **kw):
        MyStyledTextCtrl.__init__(self,*args, **kw)
        self.SetCaretForeground('BLACK')
        self.SetReadOnly(True)
        self._replace=''
        self._text=''
        self.__on_update = False
    def _OnUpdate(self, evt=None, **kw):
        log(4, "MyReplaceTextCtrl.OnUpdate", "(%s, %s)", (evt, kw) )
        if evt is not None:
            log(16, 'MyReplaceTextCtrl.OnUpdate', (evt.IsCommandEvent(),evt.GetEventType(),))
        for i in ('_text','_replace','_regex'):
            if not hasattr(self, i):
                log(32, 'MyReplaceTextCtrl.OnUpdate', 'Missing %s', i)
                return
            else:
                log(32, 'MyReplaceTextCtrl.OnUpdate', '%s: %s', (i, getattr(self,i)) )
        try:
            new_text = self._regex.sub(self._replace, self._text, )
            log(256, 'MyReplaceTextCtrl.OnUpdate', 'new_text: %s', new_text)
        except Exception, e:
            log(256, 'MyReplaceTextCtrl.OnUpdate', e)
            raise
        self.SetReadOnly(False)
        self.SetText( new_text )
        self.SetReadOnly(True)
    def SetReplace(self, **kw):
        log(4, "MyReplaceTextCtrl.SetReplace", kw)
        if not kw.has_key('replace'):
            return
        replace = kw['replace']
        if self._replace != replace:
            self._replace = replace
            self.OnUpdate(caller='MyReplaceTextCtrl.SetReplace')
    def SetOriginal(self, **kw):
        log(4, "MyReplaceTextCtrl.SetOriginal", kw)
        if not kw.has_key('text'):
            return
        text = kw['text']
        if self._text != text:
            self._text = text
            self.OnUpdate(caller='MyReplaceTextCtrl.SetOriginal')

class MyReChoice(wx.Choice):
    def SetTextCtrl(self, ctrl):
        self._text_ctrl = ctrl
    def OnChange(self, evt):
        self._text_ctrl.SetReStyle(self.GetSelection)

class RECheckboxes(object):
    def __init__(self, parent):
        self._valid_flags = ['DOTALL', 'IGNORECASE', 'MULTILINE']
        for i in self._valid_flags:
            setattr(self, i, wx.CheckBox(parent, -1, i))
        self.MULTILINE.SetValue(True)
    def GetFlags(self):
        flags = 0
        for i in self._valid_flags:
            box = getattr(self, i)
            if box.GetValue():
                flags |= getattr(re, i)
        return flags
    def AddToSizer(self, sizer):
        for i in self._valid_flags:
            sizer.Add( getattr(self, i) )
    def __repr__(self):
        flags = []
        for i in self._valid_flags:
            box = getattr(self, i)
            if box.GetValue():
                flags.append('re.'+i)
        return '|'.join(flags)
    def Bind(self, frame, fcn):
        for i in self._valid_flags:
            frame.Bind(wx.EVT_CHECKBOX, fcn, getattr(self, i))

