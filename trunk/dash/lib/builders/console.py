# encoding: utf-8

###########
# ORP - Open Robotics Platform
# 
# Copyright (c) 2009 John Harrison, William Woodall
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
console.py - Builds/Contains item that live in the console frame

Created by William Woodall on 2009-11-09.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other Libraries
import lib.elements
from wx.py.shell import Shell

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

class Consoles(object):
    """Object that contains all console like windows"""
    def __init__(self, parent, mgr):
        self.parent = parent
        self.mgr = mgr
        
        # Create the AUI Notebook
        self.console = wx.aui.AuiNotebook(parent, -1, wx.DefaultPosition, wx.Size(430, 300), 
                            wx.aui.AUI_NB_DEFAULT_STYLE | wx.aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER)
                            
        # Create the Log and Shell windows
        self.createLogConsole()
        self.createShellConsole()
        
        # Add the notebook to the AUI manager
        self.mgr.AddPane(self.console, wx.aui.AuiPaneInfo().
                Name("Consoles").Caption("Console Container").Bottom().Layer(1).
                Position(0).CloseButton(True).MaximizeButton(True))
                
    def createShellConsole(self):
        """Creates the Shell Console"""
        self.console_shell = Shell(self.console, locals=locals())
        lib.elements.SHELL_CONSOLE = self.console_shell
        self.console.AddPage(self.console_shell, "Shell")
        
    def createLogConsole(self):
        """Creates the Log Console"""
        self.console_log = wx.TextCtrl(self.console, -1, "", wx.DefaultPosition, wx.DefaultSize,
                                          wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY)
        lib.elements.LOG_CONSOLE = self.console_log
        self.console.AddPage(self.console_log, "Log")
        