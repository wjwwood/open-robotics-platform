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
editor.py - Contains events and callbacks related to the editor

Created by William Woodall on 2010-11-08.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Imports  ###

# Standard Python Libraries
import sys
import os

# Other libraries
import lib.elements as elements
from lib.builders.editor import Editor

###  Functions  ###

def newFile(event, title=None, text="", file_type=None):
    """Opens a new window in the editor"""
    editor = Editor(elements.MAIN, elements.MAIN._mgr, title=title, text=text, file_type=file_type)
    editor.Show()
    
def openFile(event, file=None):
    """Opens a file, if the file isn't given, prompts the user"""
    pass
    
def save(event):
    """Saves the currently selected file in the editor"""
    pass
    
def close(event):
    """Closes the currently selected file int he editor"""
    child = elements.MAIN.GetActiveChild()
    if child != None:
        child.Close(True)