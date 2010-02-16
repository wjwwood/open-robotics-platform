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
menu.py - Contains events and callbacks related to general menu functions

Created by William Woodall on 2009-11-08.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2009 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other Libraries
from lib.elements import *
import lib.elements as elements
import lib.events.remotecontrol as rc

###  Functions  ###

def quit(event):
    """Quits the Dashboard"""
    if rc.ps3 != None:
        rc.toggle()
    MAIN.Close(True)
    sys.exit()
    
def toggleProjectDrawer(event):
    """This will toggle the Project Drawer hidden/shown"""
    pass
    
def openLRFData(event):
    """Opens the LRF data view"""
    sys.path.append('widgets')
    import lrf
    l = lrf.getWidget()(MAIN, -1, elements.TOOLBAR.server_addr.GetValue())
    MAIN._mgr.AddPane(l)
    MAIN._mgr.GetPane(l).Float()
    MAIN._mgr.Update()