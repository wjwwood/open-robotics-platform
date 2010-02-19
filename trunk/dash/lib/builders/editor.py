#!/usr/bin/env python -OO
# encoding: utf-8

###########
# ORP - Open Robotics Platform
# 
# Copyright (c) 2010 John Harrison, William Woodall
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##########

"""
editor.py - Contains/Builds Editor

Created by William Woodall on 2010-11-08.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other Libraries
import lib.elements
from lib.elements import *
from vendor.styled_text_ctrl import PyCodeEditor

try: # try to catch any missing dependancies
# wx for window elements
    PKGNAME = 'wxpython'
    import wx
    import wx.aui as aui

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
            module, try 'easy_install "+PKGNAME+"', else consult google.")

###  Class  ###

class Editor(wx.aui.AuiMDIChildFrame):
    """Main Content Editor"""
    def __init__(self, parent, mgr, title=None, text="", file_type='normal'):
        # Set the File Type
        self.file_type = file_type
        self.path = None
        # Prepare the title
        if title == None:
            if parent.count == 1:
                title = "Untitled"
            else:
                title = "Untitled %d" % parent.count
            parent.count += 1
        else:
            self.path = title
            _, title = os.path.split(self.path)
        # Call super init
        wx.aui.AuiMDIChildFrame.__init__(self, parent, -1,
                                         title=title)
        self.parent = parent
        self.mgr = mgr
        
        # Set the Saved flag
        self.saved = True
        
        # Create the Styled Text Control
        self.text_ctrl = PyCodeEditor(self, wx.NO_BORDER | wx.TE_MULTILINE)
        self.text_ctrl.SetValue(text)
        
        # Add it to a sizer
        sizer = wx.BoxSizer()
        sizer.Add(self.text_ctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        # Do layout later
        wx.CallAfter(self.Layout)
        