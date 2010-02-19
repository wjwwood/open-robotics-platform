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
elements.py - Contains all the major elements of the GUI for ease of access

Created by William Woodall on 2010-11-02.
"""
__author__ = "William Woodall"
__copyright__ = "Copyright (c) 2010 John Harrison, William Woodall"

###  Variables  ###

# Main Frame
MAIN = None

# Remote server object
REMOTE_SERVER = None

# Menus
MENUS = None
FILE_MENU = None

# Project Drawer
PROJECT_DRAWER = None

# Toolbars
TOOLBAR = None
LOCAL_FILE_TOOLBAR = None
REMOTE_FILE_TOOLBAR = None
REMOTE_SERVER_TOOLBAR = None
CONTROL_CODE_TOOLBAR = None

# Status Bar
STATUS_BAR = None

# Consoles
CONSOLE = None
SHELL_CONSOLE = None
LOG_CONSOLE = None