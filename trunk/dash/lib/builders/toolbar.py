#!/usr/bin/env python -OO
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
toolbar.py - Contains the construction of the toolbar

Created by William Woodall on 2009-10-30.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other Libraries
import lib.elements
import lib.events.localfiles as localfiles
import lib.events.servermanagement as servermanagement
import lib.events.remotefiles as remotefiles
import lib.events.controlcode as controlcode
import lib.events.remotecontrol as remotecontrol

try: # try to catch any missing dependancies
# wx for window elements
    PKGNAME = 'wxpython'
    import wx
    import wx.aui as aui

    del PKGNAME
except ImportError as PKG_ERROR: # We are missing something, let them know...
    sys.stderr.write(str(PKG_ERROR)+"\nYou might not have the "+PKGNAME+" \
            module, try 'easy_install "+PKGNAME+"', else consult google.")


###  Classes  ###
class Toolbars:
    """Class containing Toolbars"""
    def __init__(self, parent, mgr):
        self.parent = parent
        self.mgr = mgr
        
        # Create the toolbars (they are added in reverse order)
        self.createControlCodeToolbar()
        self.createRemoteFileToolbar()
        self.createLocalToolbar()
        self.createRemoteServerToolbar()
        self.createSyncToolbar()
        
        # Link to elements
        lib.elements.TOOLBAR = self
        
    def createSyncToolbar(self):
        self.sync_tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, wx.TB_FLAT | wx.TB_NODIVIDER)
        
        self.sync_button = wx.Button(self.sync_tb, -1, 'Sync')
        self.sync_tb.AddControl(self.sync_button)
        self.sync_button.Enabled = False
        
        self.sync_tb.Realize()
        self.mgr.AddPane(self.sync_tb, aui.AuiPaneInfo().Name("Sync File").
                    Caption("Local File Operations").ToolbarPane().Top().Row(2))
        
    def createLocalToolbar(self):
        """Creates the Local Toolbar"""
        ## Local operations on Current file ##
        # Create tool bar
        self.local_tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize,
                                        wx.TB_FLAT | wx.TB_NODIVIDER)
        lib.elements.LOCAL_FILE_TOOLBAR = self.local_tb
        
        # Save Button
        self.save_button = wx.Button(self.local_tb, -1, 'Save')
        self.local_tb.AddControl(self.save_button)
        self.save_button.Bind(wx.EVT_BUTTON, localfiles.saveFile)
        
        # Run Locally
        self.run_locally_button = wx.Button(self.local_tb, -1, 'Run Locally')
        self.run_locally_button.Disable()
        self.local_tb.AddControl(self.run_locally_button)
        self.run_locally_button.Bind(wx.EVT_BUTTON, localfiles.runLocally)
        
        # Add the toolbar to the aui manager
        self.local_tb.Realize()
        self.mgr.AddPane(self.local_tb, aui.AuiPaneInfo().Name("Local File").
                    Caption("Local File Operations").ToolbarPane().Top().Row(1))
                    
    def createRemoteServerToolbar(self):
        """Creates the Remote Server Toolbar"""
        ## Remote Server Management ##
        # Create Toolbar
        self.server_tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, 
                                        wx.TB_FLAT | wx.TB_NODIVIDER)
        lib.elements.REMOTE_SERVER_TOOLBAR = self.server_tb
        
        # Connect/Disconnect Button
        self.connect_button = wx.Button(self.server_tb, -1, "Connect", size=(100,-1))
        self.server_tb.AddControl(self.connect_button)
        self.connect_button.Bind(wx.EVT_BUTTON, servermanagement.connect)
        
        # Server Address Text Box
        self.server_addr = wx.TextCtrl(self.server_tb, -1, "localhost", size=(-1,-1))
        self.server_tb.AddControl(self.server_addr)
        
        # Restart Button
        self.restart_button = wx.Button(self.server_tb, -1, "Restart", size=(-1,-1))
        self.restart_button.Disable()
        self.server_tb.AddControl(self.restart_button)
        self.restart_button.Bind(wx.EVT_BUTTON, servermanagement.restart)
        
        # Shutdown Button
        self.shutdown_button = wx.Button(self.server_tb, -1, "Shutdown", size=(-1,-1))
        self.shutdown_button.Disable()
        self.server_tb.AddControl(self.shutdown_button)
        self.shutdown_button.Bind(wx.EVT_BUTTON, servermanagement.shutdown)
        
        # R/C Button
        self.RC_button = wx.Button(self.server_tb, -1, "Turn on R/C", size=(-1,-1))
        self.RC_button.Disable()
        self.server_tb.AddControl(self.RC_button)
        self.RC_button.Bind(wx.EVT_BUTTON, remotecontrol.toggle)
        
        # Add the toolbar to the aui manager
        self.server_tb.Realize()
        self.mgr.AddPane(self.server_tb, aui.AuiPaneInfo().Name("Remote Server").
                    Caption("Remote Server Management").ToolbarPane().Top().Row(1))
                    
    def createRemoteFileToolbar(self):
        """Create Remote File Toolbar"""
        ## Remote File Management ##
        # Create Toolbar
        self.remote_tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, 
                                        wx.TB_FLAT | wx.TB_NODIVIDER)
        lib.elements.REMOTE_FILE_TOOLBAR = self.remote_tb
        
        # Send File Button
        self.send_button = wx.Button(self.remote_tb, -1, "Send", size=(-1,-1))
        self.send_button.Disable()
        self.remote_tb.AddControl(self.send_button)
        self.send_button.Bind(wx.EVT_BUTTON, remotefiles.send)
        
        # Configure Robot Button
        self.config_button = wx.Button(self.remote_tb, -1, "Configure Robot", size=(-1,-1))
        self.config_button.Disable()
        self.remote_tb.AddControl(self.config_button)
        self.config_button.Bind(wx.EVT_BUTTON, remotefiles.openConfig)
        
        # Add the toolbar to the aui manager
        self.remote_tb.Realize()
        self.mgr.AddPane(self.remote_tb, aui.AuiPaneInfo().Name("Remote Files").
                    Caption("Remote File Management").ToolbarPane().Top().Row(2))
                    
    def createControlCodeToolbar(self):
        """Creates the Control Code Toolbar"""
        ## Execution of Control Code
        # Create Toolbar
        self.cc_tb = wx.ToolBar(self.parent, -1, wx.DefaultPosition, wx.DefaultSize, 
                                        wx.TB_FLAT | wx.TB_NODIVIDER)
        lib.elements.CONTROL_CODE_TOOLBAR = self.cc_tb
        
        # Add the Run Button
        self.run_button = wx.Button(self.cc_tb, -1, "Run")
        self.run_button.Disable()
        self.cc_tb.AddControl(self.run_button)
        self.run_button.Bind(wx.EVT_BUTTON, controlcode.run)
        
        # Add the Pause Button
        self.pause_button = wx.Button(self.cc_tb, -1, "Pause")
        self.pause_button.Disable()
        self.cc_tb.AddControl(self.pause_button)
        self.pause_button.Bind(wx.EVT_BUTTON, controlcode.pause)
        
        # Add the Stop Button
        self.stop_button = wx.Button(self.cc_tb, -1, "Stop")
        self.stop_button.Disable()
        self.cc_tb.AddControl(self.stop_button)
        self.stop_button.Bind(wx.EVT_BUTTON, controlcode.stop)
        
        # Add the toolbar to the aui manager
        self.cc_tb.Realize()
        self.mgr.AddPane(self.cc_tb, aui.AuiPaneInfo().Name("Control Code").
                    Caption("Control Code Control").ToolbarPane().Top().Row(2))