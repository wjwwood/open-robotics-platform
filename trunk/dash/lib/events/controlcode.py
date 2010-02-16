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
controlcode.py - Contains methods related to controling control code

Created by William Woodall on 2009-11-04.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other libraries
import lib.elements as elements

import wx

###  Functions  ###

def run(event):
    """Runs the currently open control code on the server"""
    editor = elements.MAIN.GetActiveChild()
    _, path = editor.path.split(os.getcwd())
    if path[0] == '/':
        path = path[1:]
    if elements.REMOTE_SERVER.runControlCode(path):
        elements.MAIN.log.info('Ran successfully')
    else:
        elements.MAIN.log.warn('File not found')
    elements.TOOLBAR.pause_button.Enable()
    elements.TOOLBAR.stop_button.Enable()
    
def pause(event):
    """Pauses the currently running control code"""
    elements.REMOTE_SERVER.pauseControlCode()
    elements.TOOLBAR.pause_button.SetLabel('Resume')
    elements.TOOLBAR.pause_button.Bind(wx.EVT_BUTTON, resume)
    
def resume(event):
    """Resumes the control code if it is paused"""
    elements.REMOTE_SERVER.resumeControlCode()
    elements.TOOLBAR.pause_button.SetLabel('Pause')
    elements.TOOLBAR.pause_button.Bind(wx.EVT_BUTTON, pause)
    
def stop(event):
    """Stops the control code forcefully"""
    elements.REMOTE_SERVER.stopControlCode()
    elements.TOOLBAR.stop_button.Disable()
    elements.TOOLBAR.pause_button.Disable()
