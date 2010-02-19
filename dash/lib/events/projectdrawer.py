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
projectdrawer.py - Contains events and callbacks related to the project drawer

Created by William Woodall on 2010-11-08.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other Libraries
import lib.elements as elements
from lib.events.editor import newFile

###  Functions  ###

def selected(event):
    """Called when an item in the porject drawer is selected"""
    event.Skip()
    
def expansionStateChanged(event):
    """Called when a folder is expanded or collapsed"""
    tree = event.GetEventObject()
    state_file = open(os.path.join(elements.MAIN.app_runner.usr_home, 'expansion.state'), 'w+')
    import pickle
    pickle.dump(tree.GetExpansionState(), state_file)
    event.Skip()
    
def activated(event):
    """Called when an item is double clicked, opens it if it is a file"""
    item = event.GetItem()
    tree_ctrl = event.GetEventObject()
    if item:
        filename, _ = tree_ctrl.GetItemPyData(item)
        if os.path.isfile(filename):
            text = open(filename).read()
            newFile(None, title=filename, text=text)